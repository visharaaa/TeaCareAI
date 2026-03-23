# Tea Disease Analysis and Recovery Platform

This project is a Flask-based web application for tea leaf disease analysis. It combines:

- Computer vision for disease detection from uploaded leaf images
- RAG-powered treatment recommendations
- A recovery-tracking model for follow-up scans
- PostgreSQL-backed user accounts, field metadata, and scan history

## Tech Stack

- Backend: Flask
- Database: PostgreSQL
- Vision model: Ultralytics YOLO
- RAG: ChromaDB + Sentence Transformers + Ollama
- Recovery model: TensorFlow / Keras
- Frontend: HTML templates, CSS, and JavaScript

## Project Structure

- `main.py`: Flask app entry point
- `controller.py`: Main orchestration for prediction, persistence, and worker threads
- `auth.py`: Session and authentication helpers
- `bootstrap.py`: Database bootstrap script
- `config.py`: Environment-driven configuration
- `app/database/`: Database access and initialization scripts
- `app/services/`: ML service modules
- `templates/`: Jinja2 HTML templates
- `static/`: CSS, JS, icons, uploads

## Prerequisites

- Python 3.11+
- PostgreSQL 16+ (or Dockerized PostgreSQL)
- Ollama installed and running locally
- NVIDIA GPU + CUDA 12.8 (recommended for model performance)

If you run in CPU-only mode, you may need to replace CUDA-specific PyTorch packages in `requirements.txt`.

## Environment Variables

Start by copying `.env.example` to `.env`, then adjust values for your environment.

```powershell
Copy-Item .env.example .env
```

The `.env` file should contain at least the following keys:

```env
SECRET_KEY=change-this-to-a-strong-random-value
SESSION_LIFETIME=8

DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tea_disease_db
DEFAULT_DB_NAME=postgres

OPENWEATHERMAP_API_KEY=your_openweathermap_key
```

Notes:

- `SESSION_LIFETIME` is in hours.
- For Docker Compose, set `DB_HOST=db`.

## Required Model and Data Files

Ensure these files are present before running:

- `app/models/tea_disease_identifier_weight.pt`
- `app/models/RecoveryTracker/recovery_model.h5`
- `app/models/RecoveryTracker/scaler.pkl`
- `app/models/RecoveryTracker/feature_columns.pkl`
- `data/treatments_data.xlsx`

The repository already contains some model and vector DB assets, but if any are missing, copy them into the paths above.

## Local Setup (Without Docker)

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

3. Start PostgreSQL and ensure credentials match your `.env`.

4. Initialize schema and seed base data.

```powershell
python bootstrap.py
```

5. Pull the Ollama model used by the app.

```powershell
ollama pull llama3.1:8b
```

6. Run the app.

```powershell
python main.py
```

7. Open the application.

- http://localhost:5000

## Docker Setup

1. Create `.env` in the project root.
2. Set `DB_HOST=db` in `.env`.
3. Build and run.

```powershell
docker compose up --build
```

4. Initialize database (first run only, from another terminal).

```powershell
docker compose exec app python bootstrap.py
```

5. Open the application at http://localhost:5000.

## Core Routes

- `/`: Home page
- `/signup`: Register account
- `/login`: Sign in
- `/logout`: Sign out
- `/field/add`: Add tea field metadata
- `/analayze`: Upload leaf image and run analysis
- `/api/fields`: Get logged-in user fields
- `/api/generate-barcode`: Generate scan/chat barcode

## Troubleshooting

- Database connection errors:
	- Verify `.env` credentials and `DB_HOST`.
	- Confirm PostgreSQL is reachable on `DB_PORT`.
- Ollama errors or empty treatment text:
	- Ensure Ollama daemon is running.
	- Run `ollama pull llama3.1:8b` and retry.
- Missing model/scaler files:
	- Place files in the exact paths listed in Required Model and Data Files.
- Upload or static file issues:
	- Ensure `static/uploaded_leaves/` is writable.

## Development Notes

- Worker threads for vision, RAG, and recovery models are started in `controller.py` at import time.
- The analyze route is intentionally named `/analayze` to match current templates and frontend calls.
- Database schema creation SQL is in `app/database/init_db/create_tables.sql`.

