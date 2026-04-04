# TeaCareAI
TeaCareAI is a full-stack intelligence platform tailored for tea farmers and agronomists, specifically designed to address tea leaf diseases in Sri Lanka and beyond. 

By taking an ordinary smartphone picture of a tea leaf, the application leverages deeply trained vision models and Retrieval-Augmented Generation (RAG) to precisely evaluate tea leaf health, provide real-time treatment guidance, and track the recovery progress of affected fields over time.

## Key Features

### 1. Leaf Status Verification & Disease Detection
- **Leaf Verifier (`leaf_verifier.py`)**: Pre-validates uploaded images to ensure they represent a valid tea leaf, minimizing false positives on stray photos.
- **Disease & Severity Identification (`tea_disease_identifier.py`)**: Employs an Ultralytics YOLO (PyTorch) model (`tea_disease_identifier_weight.pt`) to detect the specific disease (e.g., Blister Blight, Pestalotiopsis) and calculate the percentage of leaf infection/severity.

### 2. Context-Aware Treatment Recommendations (RAG)
- **RAG Engine (`treatment_recommendations.py`)**: Uses a local Vector Database (ChromaDB + SentenceTransformers `BAAI/bge-small-en-v1.5`) mapped to a localized treatment repository.
- **Natural Language Explanations**: Uses Ollama running `llama3.1:8b` right on the edge to turn agriculture knowledge into actionable advice for the farmer—working entirely offline if needed.

### 3. Analytics & Recovery Tracking
- **Post-treatment Tracking (`recovery_tracker.py`)**: Associates scans using a unique chat/scan barcode. Uses a TensorFlow/Keras Neural Network (`recovery_model.h5`) to analyze sequential data and deduce whether a plant's health is "Improving," "Deteriorating," "Stable," or "New."
- **Field Management**: Geo-tags and tracks crop elevation, tea variety, and plant age for aggregate analytics across the property.

---

## Architecture & Project Structure

The project relies on a modular Flask backend interfaced with independent machine learning services, bound together by a robust PostgreSQL data management tier.

```text
TeaCareAI/
├── app.py                     # Flask application routes
├── main.py                    # Entry point: runs pre-flight constraints, then launches Flask
├── controller.py              # Business logic coordinating services & DB operations
├── auth.py                    # Session management and generic auth mechanisms
├── bootstrap.py               # Creates target DB schema & primes the LLM
├── check_constraints.py       # Ensures Python version, Ollama, & DB are active before startup
├── config.py                  # Environment variable validations & configuration objects
├── pyproject.toml / requirements.txt # Python dependencies
├── docker-compose.yml / Dockerfile   # Containerization config for the stack
├── app/
│   ├── database/              # Data models, DB initializations SQL (`create_tables.sql`)
│   ├── models/                # YOLO Weights (.pt) and TF Models (.h5, .pkl scalers)
│   └── services/              # Core ML processing APIs (RAG, Inference, Tracker)
├── data/                      # Raw Datasets & Chroma SQLite KB files
├── scripts/                   # Model Retraining Notebooks, retriever tests (`testing.py`)
├── static/                    # Frontend Assets (CSS, JS, Icons) + Image Uploads
└── templates/                 # Rendered UI Views (`index.html`, `analayze.html`, etc.)
```

---

## Getting Started

### Prerequisites
- **Python:** 3.11.x
- **PostgreSQL:** Version 14+ (Ensure a user is set up and permitted)
- **Ollama:** Installed and actively running locally (with the selected model pulled)

### Local Development Setup (Windows PowerShell)

1. **Clone & Virtual Environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies**
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
   If you do have a CUDA-compatible setup, use `requirements_cuda.txt` alternatives carefully and pin versions as needed for your machine.

3. **Environment Variables**
   ```powershell
   Copy-Item .env.example .env
   ```
   *Modify the new `.env` file to match your PostgreSQL credentials (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME), the OPENWEATHERMAP_API_KEY, and ensure LLM_NAME / EMBEDDING_MODEL are aligned.*

4. **Pull Local LLM Model**
   ```powershell
   ollama pull llama3.1:8b
   ```

5. **Initialize Database & RAG Check**
   ```powershell
   python bootstrap.py
   ```

6. **Start Application Server**
   ```powershell
   python main.py
   ```
   *Access the web app at `http://localhost:5000`*

### Docker Deployment

To spin up the entire application enclosed securely in its own environment with a managed Postgres container:

```powershell
# Set DB_HOST=db in your .env before proceeding
docker compose up --build
```
On the very first launch, open a terminal into the container to run the bootstrap process:
```powershell
docker compose exec app python bootstrap.py
```

---

##  Routes & User Flow

- **Account Handling:** Users sign up (`/signup`) or log in (`/login`) tracking device telemetry.
- **Fields:** Users manage their geographical plots of tea via `/field/add` specifying variety and age.
- **Analyze Dashboard:** Accessed via `/analayze`, farmers upload their images.

---

##  Background Jobs & Development Scripts

The `/scripts/` folder houses research and ops protocols:
- `train_model.py`: Pipeline for updating the Keras recovery timeline model.
- `report_generator.ipynb`: Notebook analyzing historical dataset aggregates.
- `retriever_correctness.py`: Utility testing chroma extraction vs. expected ground truths for debugging.


