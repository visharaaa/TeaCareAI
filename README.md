# TeaCareAI

TeaCareAI is a Flask-based platform for tea leaf disease detection, treatment recommendation, and treatment progress tracking.

The system combines:

- YOLO-based tea disease detection from leaf images
- RAG-based treatment generation (ChromaDB + SentenceTransformer + Ollama)
- Recovery status prediction using a TensorFlow model
- PostgreSQL-backed auth, fields, scan history, and session token management

## Current Flow

1. User signs up/logs in.
2. User registers field details.
3. User uploads a leaf image in Analyze.
4. Model predicts disease, severity, infection percentage, and lesion metadata.
5. RAG retrieves treatment context and Ollama generates farmer-friendly guidance.
6. Follow-up scans on the same chat barcode calculate recovery trend (`new`, `improving`, `stable`, `deteriorating`).

## Tech Stack

- Backend: Flask 3
- Database: PostgreSQL 17
- Vision model: Ultralytics YOLO (PyTorch)
- RAG: ChromaDB + SentenceTransformers + Ollama
- Recovery model: TensorFlow / Keras
- Frontend: Jinja templates + JS + CSS

## Project Structure

- `main.py`: Startup entrypoint (runs preflight checks, then starts app)
- `app.py`: Flask routes and HTTP handlers
- `controller.py`: Core orchestration for prediction, RAG, and persistence
- `auth.py`: Authentication/session helpers
- `check_constraints.py`: Preflight checks for Python version, DB schema, and Ollama model
- `bootstrap.py`: One-time bootstrap for DB schema and Ollama model warm-up
- `config.py`: Environment/config mapping
- `app/database/`: DB connection, schema init, and SQL scripts
- `app/services/`: Disease detector, RAG recommender, and recovery tracker services
- `templates/`: HTML views
- `static/`: CSS, JS, and uploaded image assets

## Prerequisites

- Python 3.11.x (project targets >=3.11 and <3.13)
- PostgreSQL running and reachable
- Ollama installed and running
- Windows PowerShell (commands below)

## Environment Variables

Create `.env` from template:

```powershell
Copy-Item .env.example .env
```

Required variables (from `.env.example`):

- `SECRET_KEY`
- `SESSION_LIFETIME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DEFAULT_DB_NAME`
- `OPENWEATHERMAP_API_KEY`

Important additions used by the current code:

- `LLM_NAME` (example: `llama3.1:8b`)
- `EMBEDDING_MODEL` (example: `BAAI/bge-small-en-v1.5`)

## Required Artifacts

TeaCareAI expects these files at runtime:

- `app/models/tea_disease_identifier_weight.pt`
- `app/models/RecoveryTracker/recovery_model.h5`
- `app/models/RecoveryTracker/scaler.pkl`
- `app/models/RecoveryTracker/feature_columns.pkl`
- `data/treatments_data.xlsx`

Optional/training-only dataset referenced in config:

- `data/tea_health_dataset.xlsx`

## Local Setup and Run

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

If you do not have a CUDA-compatible setup, use `requirements_cuda.txt` alternatives carefully and pin versions as needed for your machine.

3. Configure `.env` for your local PostgreSQL and Ollama model settings.

4. Run one-time bootstrap (creates DB/schema and checks model availability via Ollama).

```powershell
python bootstrap.py
```

5. Start the application.

```powershell
python main.py
```

6. Open:

```text
http://localhost:5000
```

## Docker Setup

The repository includes a CUDA-enabled Docker setup.

1. Create `.env` and set `DB_HOST=db`.
2. Build and run services.

```powershell
docker compose up --build
```

3. (First run) initialize DB/schema and model bootstrap inside the app container.

```powershell
docker compose exec app python bootstrap.py
```

4. Open `http://localhost:5000`.

Notes:

- `docker-compose.yml` mounts `app/models` and `data/rag_kb` as volumes.
- GPU reservation is configured through Compose `deploy.resources.reservations.devices`.

## Preflight Checks

Run checks manually:

```powershell
python check_constraints.py
```

`main.py` also runs this automatically before starting Flask.

Checks include:

- Python version check
- PostgreSQL DB existence and required schema constraints
- Ollama server reachability and presence of configured model

## Routes

UI routes:

- `GET /`
- `GET /about`
- `GET|POST /login`
- `GET|POST /signup`
- `GET|POST /logout`
- `GET|POST /field/add`
- `GET|POST /analayze` (spelling in code is currently `analayze`)

API routes:

- `GET /api/fields`
- `POST /api/generate-barcode`
- `GET /api/chat-codes`

## Database

Schema script: `app/database/init_db/create_tables.sql`

Main entities:

- `users`
- `field`
- `scan_history_chat`
- `user_scan_history`
- `disease`
- `detection`
- `treatment_recommendation`
- `applied_treatment`
- `user_refresh_token`

## Troubleshooting

- App exits immediately on startup:
  - Run `python check_constraints.py` and fix the failing check.
- DB connection failures:
  - Verify `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and database existence.
- Missing Ollama model:
  - Ensure Ollama daemon is running and pull the model set in `LLM_NAME`.
- RAG returns poor/empty results:
  - Ensure `data/treatments_data.xlsx` exists and has treatment-related columns.
- Upload/prediction issues:
  - Ensure `static/uploaded_leaves` exists and is writable.

## Development Notes

- Analyze route/template naming currently uses `analayze` (`templates/analayze.html`).
- Startup chain is `main.py -> check_constraints.py -> app.py`.
- `bootstrap.py` is intended for first-time environment/database/model initialization.

