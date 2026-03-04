import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class Config:
    # 1. Flask Web App Settings
    SECRET_KEY = os.getenv("SECRET_KEY")

    # 2. Database Settings 
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    
    # Creates the full connection string
    DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # 3. YOLO Detection Settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    YOLO_MODEL_PATH = os.path.join(BASE_DIR, "app", "models", "yolo_tea_v8.pt")
    
    # Minimum confidence score for a positive disease detection
    CONFIDENCE_THRESHOLD = 0.60  

    # 4. RAG & Treatment Settings
    VECTOR_DB_PATH = os.path.join(BASE_DIR, "data", "rag_kb")