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

There are 4 components in this app:

- `database.py`, handling connection to the ATP instance.
- `generate_cohere.py`, handling connection to the GenAI service. This is exposed as a Flask web app on port **3500**..
- `synthesia.py`, handling integration with synthesia's API. This too is exposed as a Flask web app on port **3501**.
- `controller.py`, handling the automatic workflow of all three other files. API port is **3502**.

## Running components automatically

To run all components automatically, you will need 3 APIs running:

```bash
python controller.py
python generate_cohere.py
python synthesia.py
```

Every time a foosball game ends, a request is automatically sent via our K8s controller to `controller.py`, which knows to run each component sequentially: first, `database.py`, then `generate_cohere.py` and finally `synthesia.py` to produce the final video output. 

The final video URL is printed on console by `synthesia.py`. 

## Running components individually

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
