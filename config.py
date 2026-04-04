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
    MODEL_VERSION=os.getenv("LLM_NAME")
    LLM_NAME = os.getenv("LLM_NAME")
    EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL")


    # NN Model Settings
    NN_MODEL_TRAIN_DATA_PATH=os.path.join(BASE_DIR,"data", "tea_health_dataset.xlsx")
    NN_MODEL_PATH = os.path.join(BASE_DIR,"app", "models", "RecoveryTracker","recovery_model.h5")
    NN_SCALER_PATH = os.path.join(BASE_DIR,"app", "models", "RecoveryTracker","scaler.pkl")
    NN_FEATURE_COLUMNS_PATH = os.path.join(BASE_DIR,"app", "models", "RecoveryTracker","feature_columns.pkl")

    #API keys
    OPENWEATHERMAP_API_KEY=os.getenv("OPENWEATHERMAP_API_KEY")


    PYTHON_VERSION=(3,11)

    #CLIP Configurations
    CLIP_POSITIVE_LABELS=[
            "a tea leaf",
            "tea plant leaves",
            "a close up of a tea leaf",
        ]
    CLIP_NEGATIVE_LABELS=[
            # People & body parts
            "a human face",
            "a person",
            "a hand",
            "a body part",
            "a crowd of people",

            # Animals
            "an animal",
            "a dog",
            "a cat",
            "a bird",
            "an insect",

            # Vehicles & transport
            "a car or vehicle",
            "a motorcycle",
            "a truck",
            "an airplane",
            "a boat",

            # Indoor objects & furniture
            "indoor furniture",
            "a chair or table",
            "a bed or sofa",
            "a lamp or light fixture",
            "a shelf or cabinet",

            # Food & drink
            "food or drink",
            "a fruit or vegetable",
            "a cup or bottle",
            "cooked or prepared food",
            "a snack or dessert",

            # Documents & screens
            "a document or paper",
            "a book or magazine",
            "a phone or computer screen",
            "a printed label or sign",
            "a whiteboard or chalkboard",

            # Outdoor non-plant scenes
            "a building or structure",
            "a road or pavement",
            "a sky or cloud",
            "a body of water",
            "a mountain or rock",

            # Miscellaneous objects
            "a tool or machine",
            "a plastic object",
            "a fabric or clothing",
            "a bag or container",
            "electronic equipment",
        ]
    CLIP_THRESHOLD=os.getenv("CLIP_THRESHOLD")
    CLIP_MODEL=os.getenv("CLIP_MODEL")

    