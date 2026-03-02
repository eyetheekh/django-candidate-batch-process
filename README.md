# Admin SuperUser
```
username: 
admin@dj.dj

password: 
admin@dj.dj
```

# Reviewer
```
username:
reviewer1@dj.dj

password:
reviewer1@dj.dj
```

# Reviewer Admin
```
username:
reviewadmin1@dj.dj

password:
reviewadmin1@dj.dj
```

# Candidate
```
username:
candidate1@dj.dj

password:
candidate1@dj.dj
```

---

## Getting Started

### 1. Environment Configuration
Copy `.env.example` to `.env` and adjust the variables as needed:
```bash
cp .env.example .env
```
Key configurable values include:
- `EXTERNAL_BATCH_API_URL`: The URL for the target batch processing API (default: `http://127.0.0.1:8001/batch/process`)
- `MAX_BATCH_SIZE`: Number of candidates to process per batch run (default: `10`)
- `PICK_TIMEOUT_MINUTES`: Time after which a processing lock is considered stale (default: `10`)
- `SCHEDULED_BEAT_INTERVAL`: Interval in seconds for the Celery Beat scheduler (default: `120`)

### 2. Local Setup (Without Docker)
Make sure you have `uv` installed.
```bash
# Sync dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Migrate the database
make migrate

# Seed the database with dummy data
make seed

# Run the Django development server
make run
```
You will also need to start Celery worker and beat in separate terminals:
```bash
uv run celery -A config worker -l info
uv run celery -A config beat -l info
```

### 3. Docker Production Architecture

                          ┌─────────────────────┐
                          │       Traefik       │
                          │  Reverse Proxy +    │
                          │  TLS + Routing      │
                          └─────────┬───────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
          ┌─────────▼─────────┐            ┌─────────▼─────────┐
          │       Web         │            │      Flower       │
          │ Django + Gunicorn │            │ Celery Monitoring │
          │ Port: 8000        │            │ Port: 5555        │
          └─────────┬─────────┘            └─────────┬─────────┘
                    │                                │
                    │                                │
          ┌─────────▼─────────┐            ┌─────────▼─────────┐
          │      Worker       │            │       Beat        │
          │ Celery Workers    │            │ Celery Scheduler  │
          └─────────┬─────────┘            └─────────┬─────────┘
                    │                                │
                    └───────────────┬────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │       Redis       │
                          │  Message Broker   │
                          │  Cache Storage    │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │     Postgres      │
                          │  Primary DB       │
                          └─────────┬─────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
          ┌─────────▼─────────┐            ┌─────────▼─────────┐
          │     Migrater      │            │      Seeder       │
          │ Django Migrations │            │ Seed Initial Data │
          └───────────────────┘            └───────────────────┘


#### Data Volumes
- postgres_data → Persistent DB storage
- redis_data → Redis persistence
- celerybeat_data → Celery beat schedule persistence

#### Network
- candidate_ingestion_batch_processing (default network)

The project utilizes a robust production-grade architecture defined in `docker-compose.yml`:
- **Traefik**: Acts as a reverse proxy, load balancer, and SSL termination endpoint. Auto-discovers containers.
- **Django Applications**: The `web` container runs on `gunicorn` behind Traefik.
- **Background Tasks**: Separate containers for `worker` and `beat`.
- **Initialization**: Dedicated short-lived containers (`migrater` and `seeder`) automatically execute schema migrations and seed dummy data asynchronously before the web container hits live status.
- **Monitoring**: Celery `flower` dashboard securely nested behind Traefik.

Run the entire cluster gracefully:
```bash
docker-compose up --build
```
*Note: Since the `seeder` container is baked into the deployment orchestration, there is no need to manually run `make seed` or `make migrate` logic. The system initializes it automatically!*

---

## Using the Seed Command
To generate dummy users and candidates, you can run the custom seed command. The command reads from the `--candidates` parameter (default is 1000). To run it via Makefile:
```bash
make seed
```
Or manually via Django management command:
```bash
python manage.py seed --candidates=100
```
This is extremely useful when testing data pagination, analytics metrics, and the batch processing queue heavily.

---

## Comprehensive Documentation
For a full detailed description of how the Batch Processor utilizes Row-Level Locking, Authentication details, or API request schemas, please see **[DOCUMENTATION.md](./DOCUMENTATION.md)**.
