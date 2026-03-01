# MSigma Candidate Processing System
## Exhaustive Project Documentation

### Table of Contents
1. [Project Objective & Overview](#1-project-objective--overview)
2. [Technology Constraints & Choices](#2-technology-constraints--choices)
3. [Architecture and Codebase Structure](#3-architecture-and-codebase-structure)
4. [Data Models & Schema](#4-data-models--schema)
5. [Authentication & Role-Based Access Control (RBAC)](#5-authentication--role-based-access-control-rbac)
6. [Data Ingestion & Validation](#6-data-ingestion--validation)
7. [External Batch Processing (Job Queue)](#7-external-batch-processing-job-queue)
8. [API Endpoints Reference](#8-api-endpoints-reference)
9. [Running the Application (Docker & Bare Metal)](#9-running-the-application)
10. [Make Commands Utility](#10-make-commands-utility)

---

### 1. Project Objective & Overview
The objective of this project is to design, implement, and justify a production-ready Candidate Processing System. The platform is designed for ingesting candidate data through form submissions and reliably synchronizing them via a batch-processing mechanism to an external service. 

The focus is heavily placed on **correctness**, **fault tolerance**, **clarity of implementation**, and **clean architecture**.

To satisfy the requirements, the system exposes a robust REST API using Django REST Framework (DRF) alongside a classic Django Server-Side Rendered (SSR) web interface for administrators.

---

### 2. Technology Constraints & Choices

- **Language:** Python
- **Web Framework:** Django (>=6.0.2) + Django REST Framework (DRF)
- **Database:** PostgreSQL (for Docker/Production) & SQLite3 (for local development)
- **Background Processing:** **Celery + Redis**
  - *Justification:* Celery, paired with Redis, is chosen over Django-Q and RQ because it is the industry standard for distributed task queues in Python. It offers unparalleled resilience, native scheduling via Celery Beat, advanced retry mechanisms with exponential backoff, and robust concurrency handling. When scaling to multiple workers, Celery provides the strongest guarantees for locking and task routing. Redis serves as an extremely fast, lightweight, and reliable message broker and results backend.
- **Authentication:** JWT via `djangorestframework-simplejwt`
- **Documentation:** OpenAPI 3 via `drf-spectacular`

---

### 3. Architecture and Codebase Structure
Following clean architecture principles, the platform clearly separates the RESTful API endpoints from the traditional SSR Web dashboard, while sharing the same underlying core business logic (Models and Services).

```text
msigma-django-assignment-2/
├── config/           # Django settings, root URL routing, WSGI/ASGI
├── apps/             # Core business logic, Models, SSR Templates, Forms
│   ├── core/         # Custom User models (Admin / Reviewers) and Auth
│   ├── candidates/   # Candidate entities, managers, and SSR views
│   ├── batch_runs/   # Batch job orchestration, background Celery tasks
│   └── dashboard/    # Reporting views for the Web UI
├── api/              # DRF REST API resources (ViewSets, Serializers, Schemas)
│   ├── auth/         # JWT generation, rotation, and logout endpoints
│   ├── candidates/   # Data ingestion and robust search endpoints
│   ├── batch_runs/   # REST interface for manual batch triggering/inspection
│   ├── reports/      # Reporting and analytical API endpoints
│   └── health/       # Public health check endpoint
├── Dockerfiles/      # Infrastructure definitions
├── docker-compose.yml# Orchestrates Postgres, Redis, Django, Celery, and Beat
└── Makefile          # Utility scripts for daily developer operations
```

---

### 4. Data Models & Schema

The data schema is designed not only to meet the core requirements but also includes robust failure-safety features like Soft Deletes.

#### 4.1 Users (`apps.core.User`)
A Custom `AbstractBaseUser` acting as the primary auth model.
*   **Fields:** `id` (UUID), `email` (login field), `password`, `role`.
*   **Roles:** Contains either `ADMIN` or `REVIEWER`. Uses robust DRF permission classes (`IsAdminOrReadOnly`) and UI decorators (`@role_required`).

#### 4.2 Candidate (`apps.candidates.Candidate`)
Represents the core entity ingested into the system.
*   **Fields:** `id` (UUID), `name`, `email`, `phone_number`, `link`, `dob`, `status`, `attempt_count`, `last_attempt_at`, `picked_at`.
*   **Safeguards (Soft Delete):** Implements `is_deleted` and `deleted_at`. Accidental data loss is prevented. A custom manager `CandidateManager` abstracts away deleted items unless explicitly requested.
*   **Status Lifecycle:** Transitions dynamically: `PENDING` -> `PROCESSING` -> `SUCCESS` or `FAILED`.

#### 4.3 Batch Run Ecosystem (`apps.batch_runs.models`)
Provides complete system auditability for the Job Queue.
*   **`BatchRun`**: Summarizes a batch attempt. Maintains state of job execution: `scheduled_for`, `started_at`, `finished_at`, `batch_size`, `success_count`, `failed_count`, `status` (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `PARTIAL`).
*   **`CandidateAttempt`**: A highly granular audit log. Maps exactly which candidate was tried in which batch (`candidate_id`, `batch_run_id`). Fields include `attempt_no`, `result_status`, and `error_message`.

---

### 5. Authentication & Role-Based Access Control (RBAC)

The system relies on JSON Web Tokens (JWT) for the API endpoints (excluding `/auth/` and `/health/`).
*   **Token Expiry & Refresh:** We implement a short-lived Access Token (15-24 minutes) paired with a longer-lived Refresh Token (1 day). Blacklisting is enabled post-rotation.
*   **Role-Based Access Control:**
    *   **ADMIN:** Granted full read and write access. Mutates candidate state, manually triggers batch runs, and can generate reports.
    *   **REVIEWER:** Granted safe read-only access. Can access reporting and analytical endpoints, perform candidate searches, inspect batches, but cannot mutate data.

---

### 6. Data Ingestion & Validation

**Endpoint:** `POST /api/candidates/`
The API requires data formatted strictly and validated by DRF serializers.
*   `name`: Validated to be non-empty string.
*   `email`: Enforced as a structurally valid email. Handled uniquely (blocks duplicates - returning 409 Conflict).
*   `phoneNumber`: Accepts robust formatted strings supporting multiple country codes (validated via Regex/Django validators).
*   `link` (Optional): DRF `URLField` validates safe URL format.
*   `dob` (Optional): DRF `DateField` strict validation.

---

### 7. External Batch Processing (Job Queue)

The core value proposition of the system handles concurrency gracefully via a Celery beat scheduler. The underlying logic handles task orchestration robustly:

*   **Location:** `apps/batch_runs/services.py` 
*   **Rules & Concurrency Guarantees:** 
    1.  **Row-Level Locking:** Executes `select_for_update(skip_locked=True)` on a chunk of the required Batch Size (`MAX_BATCH_SIZE = 10` logically mapping). This ensures zero race conditions—no two celery workers will ever pull the same candidate.
    2.  **State Marker:** Immediately upon locking, candidates are marked with a `picked_at` timestamp.
    3.  **Resilience & Safe Restarts:** Every batch cycle actively hunts for "stale" locks (e.g., `picked_at` older than X minutes, representing a worker crash) and releases them back into the `PENDING` pool.
    4.  **Integration constraints:** Sends the strict payload format (`{id, name, email, phoneNumber, link, dob}`) exactly as requested to the external API endpoint.
    5.  **State transitions:** Automatically tags candidates with `SUCCESS` or `FAILED`, increments the `attempt_count`, and triggers retry behavior for `FAILED` entities in subsequent batches. `SUCCESS` entities are completely filtered out of future lock scopes.

---

### 8. API Endpoints Reference

All endpoints return mapped explicit status codes mapping to standard errors (400, 401, 403, 404, 409).
*(Full interactive Swagger documentation is available at `<DOMAIN>/api/docs/` once running)*

#### Authentication APIs
1.  `POST /api/auth/login/` - Takes `{email, password}`. Returns `{access, refresh}`.
2.  `POST /api/auth/refresh/` - Takes `{refresh}` token. Returns new token pairs.
3.  `POST /api/auth/logout/` - Blacklists outstanding tokens.

#### Candidate APIs
4.  `POST /api/candidates/` **(ADMIN ONLY)** - Creates a single candidate entity. Handles duplicates.
5.  `GET /api/candidates/search` **(ADMIN, REVIEWER)** - Complex search abstraction over candidates:
    *   **Query Params:** `q` (Name/Email text search), `status` (array list), `createdFrom`, `createdTo`, `hasLink`, `minAttempts`, `sort` (`recent`, `attempts_desc`, `status_then_recent`), `page`, `pageSize`.
    *   **Response:** Paginated JSON envelope yielding matching candidates.

#### Reporting APIs
6.  `GET /api/reports/status-metrics` **(ADMIN, REVIEWER)** - Analytical endpoint fetching aggregate statistics, timeline analysis (`groupBy=day|week`), attempt averages, retry histograms, and email domain distribution.
7.  `GET /api/reports/stuck-candidates` **(ADMIN, REVIEWER)** - Identifies candidates needing manual attention. Looks for `FAILED` items above an attempt threshold (`N`) over an elapsed time (`X`), or ignored `PENDING` candidates over time (`Y`).

#### Batch Execution APIs
8.  `GET /api/batch_runs/` **(ADMIN, REVIEWER)** - Paginated historical list of all batch operations.
9.  `POST /api/batch_runs/trigger/` **(ADMIN ONLY)** - Manually executes a single batch sequence dynamically overriding the queue scheduler for immediate execution up to the batch limit of 10.

#### General System
10. `GET /api/health/` **(PUBLIC)** - System UP verification (checks DB and broker access).

---

### 9. Running the Application

The project heavily embraces containerization for frictionless deployment.

#### Method 1: Docker Compose (Preferred)
```bash
docker-compose up --build
```
Orchestrates 5 interlinked containers:
-   `postgres_db` & `postgres_data` mapping.
-   `redis_cache` & `redis_data` mapping.
-   `django_web` (Django Gunicorn WSGI container bound to 0.0.0.0:8000)
-   `celery_worker` (Task execution core)
-   `celery_beat` (Scheduler daemon)

#### Method 2: Local Bare Metal Setup
```bash
# 1. Start Virtual Environment (using pip/uv):
uv sync  # Uses the provided uv.lock file
source .venv/bin/activate

# 2. Database Migrations & Seeding:
make migrate
make su  # Interactive superuser generation

# 3. Local Web Server:
make run   # Starts dev server on 127.0.0.1:8000

# 4. Starting Background Queue natively:
celery -A config worker -l info
celery -A config beat -l info
```

#### Pre-seeded Local Testing Credentials
As noted in the original standard `README.md`, testing accounts for seed verification include:
*   **Admin Base:** `admin@dj.dj` : `admin@dj.dj`
*   **Reviewer:** `reviewer1@dj.dj` : `reviewer1@dj.dj`

---

### 10. Make Commands Utility
A standard mapping tool wrapping tedious Django commands:
*   `make run` : Spawns internal webserver testing port 8000.
*   `make migrate` / `make mkmgr` : Synchronize DB schemas.
*   `make su` : Bootstraps `createsuperuser`.
*   `make test` / `make check` : Triggers Django integrated test suite validations.
