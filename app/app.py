import datetime
import json
import re
import uuid
from secrets import token_bytes

import boto3
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from boto3.dynamodb.conditions import Key
from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel

app = FastAPI()
ddb = boto3.resource('dynamodb')
enclaveTable = ddb.Table('Enclaves')
shardTable = ddb.Table('Shards')

UNAME_REGEX = re.compile("^(?!.*\.\.)(?!.*\.$)[^\W][\w.@]{0,32}$")


# TODOS:
# simplify code
# write frontend interactions
# check code

# ENCLAVE HANDLERS

class PostEnclave(BaseModel):
    type: int
    presig: str
    postsig: str
    enclave: str
    usrId: str
    id: str


@app.post('/Enclave')
def post_enclaves(enclave_form: PostEnclave):
    ftype = enclave_form.type
    # user(0)
    # spine(1)
    # key(2)
    if ftype == 0 and ftype == 1 and ftype == 2:
        digest = SHA256.new()
        presig = enclave_form.presig
        postsig = enclave_form.postsig
        enc = enclave_form.enclave
        digest.update(presig)  # get presigned txt from request
        # TODO: if you can only sign string types, you may need to convert to string here and on client

        # Load public key (not private key) and verify signature, bypass getting key if you are uploading your key for the first time
        public_key = RSA.importKey(enc) if ftype == 2 else RSA.importKey(
            enclaveTable.get_item(Key={ 'id': enclave_form.usrId, 'type': 2 }).get('Item').enclave)
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
                if UNAME_REGEX.match(enclave_form.id) is not None:
                    post_obj['id'] = enclave_form.id
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


class UpdateEnclave(BaseModel):
    signedData: str
    usrId: str
    enclave: str


@app.get('/Enclave/{id}')
def get_enclave(shard_id: str, shard_form: UpdateEnclave):
    get_patch_delete_enclave(shard_id, shard_form, "GET")


@app.patch('/Enclave/{id}')
def patch_enclave(shard_id: str, shard_form: UpdateEnclave):
    get_patch_delete_enclave(shard_id, shard_form, "PATCH")


@app.delete('/Enclave/{id}')
def delete_enclave(shard_id: str, shard_form: UpdateEnclave):
    get_patch_delete_enclave(shard_id, shard_form, "DELETE")


@app.get('/Enclave/{id}')
def get_patch_delete_enclave(enclave_id: str, enclave_request: UpdateEnclave, method: str):
    key = { 'id': enclave_id }
    enclave = enclaveTable.get_item(Key=key).get('Item')
    if enclave:
        if method == 'GET':
            return json_response(enclave)
        elif method == 'PATCH' or method == 'DELETE':
            # signed binary from client
            signed_data = enclave_request.signedData
            usr_id = enclave_request.usrId
            # this is to rotate our stuff without adding change dates, it also allows for simple key rotations
            # steps:
            # check ownership with user pubkey postsign and prevsign
            # check new signature of nextsign
            # save signature to postsign and nextsign to prevsign
            # generate key and set it
            eckeys = enclave.sigblock.split("::")

            if verify_signature(usr_id, eckeys[0], eckeys[1]):  # check user key
                if verify_signature(usr_id, eckeys[3], signed_data):  # check nextkey
                    if method == 'PATCH' and enclave_request.enclave is not None:
                        attribute_updates = { 'body': { 'Value': enclave_request.enclave, 'Action': 'PUT' },
                                              'sigblock': { 'Value': f"{eckeys[3]}::{signed_data}::{token_bytes(20)}",
                                                            'Action': 'PUT' }, }
                        enclaveTable.update_item(Key=key, AttributeUpdates=attribute_updates)
                        return json_response({ "message": "Entry updated" })
                    elif method == 'DELETE':
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

class PostShard(BaseModel):
    userid: str
    idAttach: str
    presign: str
    postsign: str
    body: str
    burnDays: str


@app.post('/Shard')
def post_shards(post_shard: PostShard):
    presig = post_shard.presig
    postsig = post_shard.postsig
    usr_id = post_shard.usrId

    if verify_signature(usr_id, presig, postsig):
        ecid = str(uuid.uuid4())
        post_obj = { 'id': ecid, 'sigblock': f"{presig}::{postsig}::{token_bytes(20)}",
                     'id_attach': post_shard.idAttach, 'body': post_shard.body }

        if 'burn_days' in post_shard and is_int(post_shard.burnDays):
            post_obj['burn_at'] = (datetime.now() + datetime.timedelta(days=post_shard.burnDays)).isoformat()

        shardTable.put_item(Item=post_obj)
        return json_response({ "id": ecid })
    else:
        return json_response({ "error": "Your init signature is phony!" }, 400)


class GetShards(BaseModel):
    upper_bound: str
    lower_bound: str


@app.get('/Shards/{shard_id}')
def get_shards(shard_id: str, form: GetShards):
    lowbound = form.lower_bound
    hibound = form.upper_bound
    shards = shardTable.query(
        KeyConditionExpression=Key('id_attach').eq(shard_id) & Key('burn_at').gte(lowbound) & Key('burn_at').lte(
            hibound)).get('Items')
    return json_response({ "posts": shards })


class UpdateShard(BaseModel):
    usrId: str
    signedData: str
    shard: str


@app.get('/Shard/{id}')
def get_shard(shard_id: str, shard_form: UpdateShard):
    get_patch_delete_shard(shard_id, shard_form, "GET")


@app.patch('/Shard/{id}')
def patch_shard(shard_id: str, shard_form: UpdateShard):
    get_patch_delete_shard(shard_id, shard_form, "PATCH")


@app.delete('/Shard/{id}')
def delete_shard(shard_id: str, shard_form: UpdateShard):
    get_patch_delete_shard(shard_id, shard_form, "DELETE")


def get_patch_delete_shard(shard_id: str, shard_form: UpdateShard, method: str):
    key = { 'id': shard_id }
    shard = shardTable.get_item(Key=key).get('Item')
    if shard:
        if method == 'GET':
            return json_response(shard)
        elif method == 'PATCH' or method == 'DELETE':
            signed_data = shard_form.signedData  # signed binary from client
            usr_id = shard_form.usrId
            # this is to rotate our stuff without adding change dates, it also allows for simple key rotations
            # steps:
            # check ownership with user pubkey postsign and prevsign
            # check new signature of nextsign
            # save signature to postsign and nextsign to prevsign
            # generate key and set it
            sikeys = shard.sigblock.split("::")

            if verify_signature(usr_id, sikeys[0], sikeys[1]):  # check user key
                if verify_signature(usr_id, sikeys[3], signed_data):  # check nextkey
                    if method == 'PATCH' and shard_form.shard is not None:
                        attribute_updates = { 'body': { 'Value': shard_form.shard, 'Action': 'PUT' },
                                              'sigblock': { 'Value': f"{sikeys[3]}::{signed_data}::{token_bytes(20)}",
                                                            'Action': 'PUT' } }
                        shardTable.update_item(Key=key, AttributeUpdates=attribute_updates)
                        return json_response({ "message": "Entry updated" })
                    elif method == 'DELETE':
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


handler = Mangum(app)


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