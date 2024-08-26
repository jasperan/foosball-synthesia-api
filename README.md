#  Python integration with Synthesia API for AI Video Generation 

To use this repo, there are two scripts. The only one you need to worry about is `synthesia.py`.

First, put your API key in a new file called `config.yaml`, with these contents:

```bash
authorization: YOUR_API_KEY
config_profile: OCI_CLI_PROFILE_NAME
compartment_id: COMPARTMENT_ID_WHERE_GENAI_SERVICE_IS_ACTIVE
```

Then, simply run:

```bash
python synthesia.py
```

You can modify all parameters of AI video generation within this script.