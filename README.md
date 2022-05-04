# paracord
a chat client you can trust. anywhere. anytime.

There is no frontend yet but soon there will be. The backend is simply an encrypted store manager, where one store is burnable and date ordered and the other isn't

Also, in the future either a longer term s3 option will be added for file hosting or we will add a pure peer-to-peer seeded file host system.

#Running

## setup locally
```sh
virtualenv -p python3.10 -v venv
source venv/bin/activate
pip install -r tests/requirements.txt -r app/requirements.txt
```
## test
```
pytest -v
```

## deploy
```
sam build --use-container
sam deploy --guided
```

## destroy
```
aws cloudformation delete-stack --stack-name paracord
```

## run
```
./venv/bin/uvicorn app.app:app --reload
```

# data structures

These are data structures that will exist inside shards or enclaves in their encrypted bodies, visible only to people 
with access

-Enclave structures
  - public key exchange
    ```json
      {
        "id": "same as user id in user enclave",
        "sigblock": "trust chain signature block",
        "type": 2,
        "body": "public key as bytes"
      }
    ```
  -user enclave block, user logs in by typing name, which finds this, then seeing if their password decrypts the enclave
   ```json
       {
        "id": "username typed on login(must be unique)",
        "sigblock": "trust chain signature block",
        "type": 2,
        "body": [this, but password encrypted: {
            user_id: "sjffj9efj93fj93",
            priv_key: "498380sfojdofj",
            default_uname: "gregor",
            default_status: "unhappy",
            default_pfp: [this is weird, encrypted using user pub/priv pair, decrypted and reencrypted with server keys],
            cur_notif_sock: [socket to notify person by, changes at some interval based on logins/fetches perhaps],
            memberships:[
                "server id": [
                    master_key: [master key used to unlock spine]
                    channels: [
                        "channel ID":"channel key",
                    ]
                ],
                "tsdfsdofsdafasds44343234": {
                    master_key: "sdffsdfsdfsdf343244234",
                    channels: [
                        "93rdfsdf":"sfs9fsdf90k9fkwe9f",
                        "7sdfsd7fs7df":"09sd7f98sdf7sd9",
                    ]
                }
            ]
        }]
       }
   ```

  -private key/spine membership/personal information enclave(password encrypted)
    ```json
      {
        "id": "random server id",
        "sigblock": "trust chain signature block",
        "type": 1,
        "body": {
        room_id: "tsdfsdofsdafasds44343234",
        room_enclave: [this, but member key encrypted, {
            users: [
                "sjffj9efj93fj93": {
                    name: "gregor",
                    status: "unhappy",
                    admin: true,
                    pfp: "https://xyz.abc/encryptedimg",
                    cur_notif_sock: (TEMPUNUSED)[socket to notify person by, changes at some interval based on logins/fetches perhaps]
                }
            ],
            [This is encrypted with an admin key so only admins can see it: channels: [
                "93rdfsdf": {
                    voice: false,
                    burntime: [unix time delta],
                },
                "7sdfsd7fs7df": {
                    voice: true, #when voice enabled, messages are negotiations, they don't need to be shown in a traditional way
                    burntime: [unix time delta], # burntime is also much faster
                }
            ]]
        }]
        }
      }
    ```

-Shard structures
    -shard message host
      ```json
        {
            id: "random junk",
            id_attach: "id of the channel this is posted in",
            body: "[encrypted junk, contains user ID, post time, user post text, authenticity signature, and any possible media links, or contains offer if RTC post]",
            burn_at: [unix timestamp]
        }
      ```

    

-RTC TURN signalling server for propping up large calls
[bog standard, nothin fancy here pholx]
