#  Python integration with Synthesia API for AI Video Generation 

To use this repo, there are two scripts. The only one you need to worry about is `synthesia.py`.

First, put your API key in a new file called `config.yaml`, with these contents:

```bash
authorization: YOUR_API_KEY
config_profile: OCI_CLI_PROFILE_NAME
compartment_id: COMPARTMENT_ID_WHERE_GENAI_SERVICE_IS_ACTIVE

db_username: DB_USERNAME
db_password: DB_PASSWORD
db_dsn: DB_DSN_STRING, starts with "(description= (retry_count=20)...."

```

There are 3 components in this app:

- database.py, handling connection to the ATP instance.
- generate_cohere.py, handling connection to the GenAI service. This is exposed as a Flask web app on port **3500**..
- synthesia.py, handling integration with synthesia's API. This too is exposed as a Flask web app on port **3501**.


To run every component, first spin up the Flask apps:

```bash
python generate_cohere.py
python synthesia.py
```

After executing database.py, each service will execute in order:

```bash
python synthesia.py
```

Every time you want to re-run tests, only execute database.py, making sure that the two other services are running and listening on port 3500 and 3501. 
> Also check for security list / firewall issues if you can't reach these ports.
