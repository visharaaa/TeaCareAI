import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # 1. Flask Web App Settings
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_LIFETIME=int(os.getenv("SESSION_LIFETIME"))

    # 2. Database Settings 
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DEFAULT_DB_NAME=os.getenv("DEFAULT_DB_NAME")
    
    DEFAULT_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # 3. YOLO Detection Settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    TEA_DISEASE_IDENTIFIER_MODEL_PATH = os.path.join(BASE_DIR, "app", "models","tea_disease_identifier_weight.pt")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploaded_leaves")
    
    
    # Minimum confidence score for a positive disease detection
    CONFIDENCE_THRESHOLD = 0.60  

    # 4. RAG & Treatment Settings
    VECTOR_DB_PATH = os.path.join(BASE_DIR, "data", "rag_kb")
    KB_PATH=os.path.join(BASE_DIR, "data","treatments_data.xlsx")
    MODEL_VERSION="llama3.1:8b"

    # NN Model Settings
    NN_MODEL_TRAIN_DATA_PATH=os.path.join(BASE_DIR,"data", "tea_health_dataset.xlsx")
    NN_MODEL_PATH = os.path.join(BASE_DIR,"app", "models", "RecoveryTracker","recovery_model.h5")
    NN_SCALER_PATH = os.path.join(BASE_DIR,"app", "models", "RecoveryTracker","scaler.pkl")
    NN_FEATURE_COLUMNS_PATH = os.path.join(BASE_DIR,"app", "models", "RecoveryTracker","feature_columns.pkl")

    #API keys
    OPENWEATHERMAP_API_KEY=os.getenv("OPENWEATHERMAP_API_KEY")

    LLM_NAME = "llama3.1:8b"
    PYTHON_VERSION=(3,11)

    