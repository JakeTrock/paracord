import datetime
import json
import re
import uuid
from secrets import token_bytes
from urllib import request

import boto3
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from boto3.dynamodb.conditions import Key
from flask_lambda2 import FlaskLambda

server = FlaskLambda(__name__)
ddb = boto3.resource('dynamodb')
enclaveTable = ddb.Table('Enclaves')
shardTable = ddb.Table('Shards')

UNAME_REGEX = re.compile("^(?!.*\.\.)(?!.*\.$)[^\W][\w.@]{0,32}$")


# TODOS:
# simplify code
# write frontend interactions
# check code

# ENCLAVE HANDLERS

@server.route('/Enclave', methods=['POST'])
def post_enclaves():
    ftype = request.form['type']
    # user(0)
    # spine(1)
    # key(2)
    if ftype == 0 and ftype == 1 and ftype == 2:
        digest = SHA256.new()
        presig = request.form['presig']
        postsig = request.form['postsig']
        enc = request.form['enclave']
        digest.update(presig)  # get presigned txt from request
        # TODO: if you can only sign string types, you may need to convert to string here and on client

        # Load public key (not private key) and verify signature, bypass getting key if you are uploading your key for the first time
        public_key = RSA.importKey(enc) if ftype == 2 else RSA.importKey(
            enclaveTable.get_item(Key={ 'id': request.form['usrId'], 'type': 2 }).get('Item').enclave)
        verifier = PKCS1_v1_5.new(public_key)
        if verifier.verify(digest, postsig):
            post_obj = { 'sigblock': f"{presig}::{postsig}::{token_bytes(20)}", 'body': enc }

            if ftype > 0:
                ecid = str(uuid.uuid4())
                post_obj['id'] = ecid
                enclaveTable.put_item(Item=post_obj)
                return json_response({ "id": ecid })
            else:
                # match valid username, cap at 32 len so you can't uuid inject
                if UNAME_REGEX.match(request.form['id']) is not None:
                    post_obj['id'] = request.form['id']
                    enclaveTable.put_item(Item=post_obj)
                    return json_response({ "success": True })
                else:
                    return json_response({
                        "error": "invalid name. Only use numbers, letters and . _ or @ and be less than 32 characters" },
                        400)
        else:
            return json_response({ "error": "Your init signature is phony!" }, 400)
    else:
        return json_response({ "error": "identifier number must be 0, 1 or 2" }, 400)


@server.route('/Enclave/<id>', methods=['GET', 'PATCH', 'DELETE'])
def get_patch_delete_enclave(id):
    key = { 'id': id }
    enclave = enclaveTable.get_item(Key=key).get('Item')
    if enclave:
        if request.method == 'GET':
            return json_response(enclave)
        elif request.method == 'PATCH' or request.method == 'DELETE':
            # signed binary from client
            signed_data = request.form['signedData']
            usr_id = request.form['usrId']
            # this is to rotate our stuff without adding change dates, it also allows for simple key rotations
            # steps:
            # check ownership with user pubkey postsign and prevsign
            # check new signature of nextsign
            # save signature to postsign and nextsign to prevsign
            # generate key and set it

            if verify_signature(usr_id, enclave.oldsign, enclave.signedold):  # check user key
                if verify_signature(usr_id, enclave.nextsign, signed_data):  # check nextkey
                    if request.method == 'PATCH' and request.form['enclave'] is not None:
                        attribute_updates = { 'body': { 'Value': request.form['enclave'], 'Action': 'PUT' },
                            'sigblock': { 'Value': f"{enclave.nextsign}::{signed_data}::{token_bytes(20)}",
                                          'Action': 'PUT' }, }
                        enclaveTable.update_item(Key=key, AttributeUpdates=attribute_updates)
                        return json_response({ "message": "Entry updated" })
                    elif request.method == 'DELETE':
                        enclaveTable.delete_item(Key=key)
                        return json_response({ "message": "Entry deleted." })
                    else:
                        return json_response({ "message": "Bad patch/delete request" }, 400)
                else:
                    return json_response({ "message": "You did not properly rotate your key. Please try again." }, 400)
            else:
                return json_response({ "message": "You do not own this document" }, 400)
    else:
        return json_response({ "message": "enclave not found" }, 404)


# SHARD HANDLERS

@server.route('/Shard', methods=['POST'])
def post_shards():
    digest = SHA256.new()
    presig = request.form['presig']
    postsig = request.form['postsig']
    usr_id = request.form['usrId']

    if verify_signature(usr_id, presig, postsig):
        ecid = str(uuid.uuid4())
        post_obj = { 'id': ecid, 'sigblock': f"{presig}::{postsig}::{token_bytes(20)}",
            'id_attach': request.form['id_attach'], 'body': request.form['body'] }

        if 'burn_days' in request.form and is_int(request.form['burn_days']):
            post_obj['burn_at'] = (datetime.now() + datetime.timedelta(days=request.form['burn_days'])).isoformat()

        shardTable.put_item(Item=post_obj)
        return json_response({ "id": ecid })
    else:
        return json_response({ "error": "Your init signature is phony!" }, 400)


@server.route('/Shards/<id>', methods=['GET'])
def get_shards():
    lowbound = request.form['lower_bound']
    hibound = request.form['upper_bound']
    shards = shardTable.query(
        KeyConditionExpression=Key('id_attach').eq(id) & Key('burn_at').gte(lowbound) & Key('burn_at').lte(
            hibound)).get('Items')
    return json_response({ "posts": shards })


@server.route('/Shard/<id>', methods=['GET', 'PATCH', 'DELETE'])
def get_patch_delete_shard(id):
    key = { 'id': id }
    shard = shardTable.get_item(Key=key).get('Item')
    if shard:
        if request.method == 'GET':
            return json_response(shard)
        elif request.method == 'PATCH' or request.method == 'DELETE':
            signed_data = request.form['signedData']  # signed binary from client
            usr_id = request.form['usrId']
            # this is to rotate our stuff without adding change dates, it also allows for simple key rotations
            # steps:
            # check ownership with user pubkey postsign and prevsign
            # check new signature of nextsign
            # save signature to postsign and nextsign to prevsign
            # generate key and set it

            if verify_signature(usr_id, shard.oldsign, shard.signedold):  # check user key
                if verify_signature(usr_id, shard.nextsign, signed_data):  # check nextkey
                    if request.method == 'PATCH' and request.form['shard'] is not None:
                        attribute_updates = { 'body': { 'Value': request.form['shard'], 'Action': 'PUT' },
                            'sigblock': { 'Value': f"{shard.nextsign}::{signed_data}::{token_bytes(20)}",
                                          'Action': 'PUT' } }
                        shardTable.update_item(Key=key, AttributeUpdates=attribute_updates)
                        return json_response({ "message": "Entry updated" })
                    elif request.method == 'DELETE':
                        shardTable.delete_item(Key=key)
                        return json_response({ "message": "Entry deleted." })
                    else:
                        return json_response({ "message": "Bad patch/delete request" }, 400)
                else:
                    return json_response({ "message": "You did not properly rotate your key. Please try again." }, 400)
            else:
                return json_response({ "message": "You do not own this document" }, 400)
    else:
        return json_response({ "message": "shard not found" }, 404)


def json_response(data, response_code=200):
    return json.dumps(data), response_code, { 'Content-Type': 'application/json' }


def is_int(val):
    try:
        num = int(val)
    except ValueError:
        return False
    return True


# https://gist.github.com/aellerton/2988ff93c7d84f3dbf5b9b5a09f38ceb


def verify_signature(usr_id, presig, postsig):
    # find newest record less than the biggest date, aka newest unsigned sig
    usrkey = enclaveTable.get_item(Key={ 'id': usr_id, 'type': 2 }).get('Item').enclave
    digest = SHA256.new()
    digest.update(presig)
    # TODO: if you can only sign string types, you may need to convert to string here and on client

    # Load public key (not private key) and verify signature
    public_key = RSA.importKey(usrkey)
    verifier = PKCS1_v1_5.new(public_key)
    verified = verifier.verify(digest, postsig)
    return verified