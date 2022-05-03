# paracord
a chat client you can trust. anywhere. anytime.

There is no frontend yet but soon there will be. The backend is simply an encrypted store manager, where one store is burnable and date ordered and the other isn't

Also, in the future either a longer term s3 option will be added for file hosting or we will add a pure peer-to-peer seeded file host system.

```sh
# setup locally
virtualenv -p python3.8 -v venv
source venv/bin/activate
pip install -r tests/requirements.txt -r app/requirements.txt

# test
pytest -v

# deploy
sam build --use-container
sam deploy --guided

# destroy
aws cloudformation delete-stack --stack-name demo

# run
uvicorn app.app:app --reload
```