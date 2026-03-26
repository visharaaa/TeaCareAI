# Tea Disease Analysis and Recovery Platform

Flask web application for tea leaf disease workflows, combining:

- Image-based tea disease detection
- Treatment recommendation generation (RAG + Ollama)
- Recovery prediction for follow-up scans
- PostgreSQL-backed users, fields, and scan history

## Features

- User sign up, login, and session management
- Field registration and user-specific field retrieval
- Leaf image upload and analysis pipeline
- Treatment suggestions based on retrieval + LLM generation
- Recovery tracking model for post-treatment assessment

## Tech Stack

- Backend: Flask
- Database: PostgreSQL
- CV model: PyTorch + Ultralytics
- RAG: ChromaDB + Sentence Transformers + Ollama
- Recovery model: TensorFlow / Keras
- Frontend: Jinja templates + CSS + JavaScript

## Project Layout

- `main.py`: Flask app entry point
- `controller.py`: Main application logic and orchestration
- `auth.py`: Authentication and session utilities
- `bootstrap.py`: Database + Ollama bootstrap helper
- `check_constraints.py`: Preflight checks (database + Ollama)
- `config.py`: Environment-driven settings
- `app/database/`: DB initialization scripts and connection helpers
- `app/services/`: Disease detection, recovery, and recommendation services
- `templates/`: HTML templates
- `static/`: CSS, JS, and uploaded files

## Prerequisites

- Python 3.11+
- PostgreSQL 16+ (or Dockerized PostgreSQL)
- Ollama installed and running
- Windows PowerShell (commands below use PowerShell syntax)

Note: `requirements.txt` currently uses CUDA-targeted PyTorch wheels.

## Environment Setup

Create your environment file from the template:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` values for your machine.

## Required Environment Variables

See `.env.example` for defaults and examples.

- `SECRET_KEY`: Flask secret key
- `SESSION_LIFETIME`: Session lifetime in hours (integer)
- `DB_USER`: PostgreSQL username
- `DB_PASSWORD`: PostgreSQL password
- `DB_HOST`: PostgreSQL host (`localhost` for local, `db` for Docker Compose)
- `DB_PORT`: PostgreSQL port (usually `5432`)
- `DB_NAME`: Main database name used by the app
- `DEFAULT_DB_NAME`: Existing bootstrap database (usually `postgres`)
- `OPENWEATHERMAP_API_KEY`: Weather API key

Ollama model selection is currently configured directly in `config.py` via `Config.LLM_NAME`.

## Local Run (Without Docker)

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

3. Ensure PostgreSQL is running and your `.env` matches it.

4. Ensure Ollama is running and pull the model from `.env` if needed.

```powershell
ollama pull llama3.1:8b
```

5. Initialize database objects and seed data.

```powershell
python bootstrap.py
```

6. Start the web app.

```powershell
python main.py
```

7. Open `http://localhost:5000`.

## Docker Run

1. Create `.env` from `.env.example`.
2. Set `DB_HOST=db` in `.env`.
3. Build and run services.

```powershell
docker compose up --build
```

4. On first run, initialize schema/data in the app container.

```powershell
docker compose exec app python bootstrap.py
```

5. Open `http://localhost:5000`.

## Health/Preflight Checks

Run prerequisite checks for database constraints and Ollama model availability:

```powershell
python check_constraints.py
```

## Main Routes

- `/`: Home
- `/signup`: User registration
- `/login`: User login
- `/logout`: User logout
- `/field/add`: Register field data
- `/analayze`: Run leaf analysis
- `/api/fields`: Fetch fields for current user
- `/api/generate-barcode`: Generate a new chat barcode

## Troubleshooting

- Database errors:
  - Verify `.env` database values.
  - Confirm PostgreSQL is reachable on `DB_HOST:DB_PORT`.
- Ollama/model errors:
  - Verify Ollama daemon is running.
  - Pull the model configured in `Config.LLM_NAME`.
- Missing model/data artifacts:
  - Confirm files exist under `app/models/` and `data/` as expected by `config.py`.
- Upload issues:
  - Ensure `static/uploaded_leaves/` exists and is writable.

