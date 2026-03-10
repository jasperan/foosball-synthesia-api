# old-foosball

Legacy foosball project combining video archive storage with a Flask-based API backend for game tracking, AI-generated video summaries (Synthesia), and Cohere-powered content generation. Uses Oracle DB for game data and OCI Object Storage for video hosting.

## Components

### Python Services
- **`controller.py`** — Flask app: `POST /game_end` endpoint receives game instance data, stores to Oracle DB
- **`database.py`** — `OracleDBInterface` class wrapping `oracledb` for game data CRUD. Reads creds from `config.yaml`
- **`synthesia.py`** — Flask app: `POST /synthesia` endpoint triggers Synthesia API video generation with custom avatars, uploads to OCI Object Storage, creates pre-authenticated requests (PARs)
- **`generate_cohere.py`** — Flask app using OCI Generative AI (Cohere) via `us-chicago-1` inference endpoint for content generation
- **`video_to_bucket.py`** — Download videos and upload to OCI Object Storage bucket
- **`custom_avatar.py`** — Synthesia avatar management
- **`verify_download.py`** — Verify video download integrity

### Video Archive
- MP4 files numbered **282 through 471** (not contiguous, ~120 files with gaps)

### Tests
- `test_cohere.py` — Tests for Cohere generation
- `test_db.py` — Tests for Oracle DB interface
- `test_synthesia.py` — Tests for Synthesia integration

### Config
- `config.yaml` (not checked in) — Oracle DB creds (`db_username`, `db_password`, `db_dsn`), OCI compartment/config profile

## Dependencies

```
oci, oracledb, flask, pyyaml
```

Install: `pip install -r requirements.txt`

Requires:
- Oracle Instant Client (`oracledb.init_oracle_client()` used in thick mode)
- OCI config at `~/.oci/config`
- `config.yaml` with DB and OCI credentials

## Running

```bash
# Game controller API
python controller.py

# Synthesia video generation webhook
python synthesia.py

# Cohere content generation
python generate_cohere.py
```

## Testing

```bash
pytest test_cohere.py test_db.py test_synthesia.py -v
```
