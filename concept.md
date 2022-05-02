-public key exchange server(kvp of user id to key)
   {
       user_id: "3893940s",
       key: "key95405904595846850946"
   }

-private key/spine membership/personal information enclave(password encrypted)
    {
    user_login: "any string, can be email, etc",
    user_enclave: [this, but password encrypted: {
            user_id: "sjffj9efj93fj93",
            priv_key: "498380sfojdofj",
            default_uname: "gregor",
            default_status: "unhappy",
            default_pfp: [this is weird, encrypted using user pub/priv pair, decrypted and reencrypted with server keys],
            cur_notif_sock: (TEMPUNUSED)[socket to notify person by, changes at some interval based on logins/fetches perhaps],
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
-shard message host
    {
        id: "2348994r239cmf",
        number: 1,
        data: "[encrypted junk, contains user ID, post time, user post text, authenticity signature, and any possible media links, or contains offer if RTC post]",
        burn_at: [unix timestamp]
    }
-spine enclave host
    {
        room_id: "tsdfsdofsdafasds44343234",
        room_enclave: [this, but master key encrypted, {
            users: [
                "sjffj9efj93fj93": {
                    name: "gregor",
                    status: "unhappy",
                    admin: true,
                    pfp: "https://xyz.abc/encryptedimg",
                    cur_notif_sock: (TEMPUNUSED)[socket to notify person by, changes at some interval based on logins/fetches perhaps]
                }
            ],
            channels: [
                "93rdfsdf": {
                    voice: false,
                    burntime: [unix time delta],
                },
                "7sdfsd7fs7df": {
                    voice: true, #when voice enabled, messages are negotiations, they don't need to be shown in a traditional way
                    burntime: [unix time delta], # burntime is also much faster
                }
            ]
        }]
    }

-RTC TURN signalling server for propping up large calls
[bog standard, nothin fancy here pholx]




export interface Enclave { #user/key/spine
       id: number,
       data: binary
}

export interface MessageShard {
        id: number,
        data: string,
        burn_at: string
}

export interface MessageSpine {
    id: number,
    messages: set[string]
}


https://github.com/nikhilkumarsingh/serverless-rest-api