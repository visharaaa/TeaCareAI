# retriever_correctness.py

from sentence_transformers import SentenceTransformer
import chromadb

embedder = SentenceTransformer('BAAI/bge-small-en-v1.5')
client = chromadb.PersistentClient(path = "chroma_db_manual")
collection = client.get_or_create_collection(name = "treatments_data")

# Test cases: (query, expected_disease, expected_severity)
test_cases = [
    ("blister blight high", "Blister Blight", "High"),
    ("grey blight high", "Grey Blight", "High"),
    ("red rust medium", "Red Rust", "Medium"),
    ("brown blight low", "Brown Blight", "Low"),
    ("thaveesha", None, None),
    ("car engine", None, None),
    ("blistr blite hi", "Blister Blight", "High"),
    ("gray blight high", "Grey Blight", "High"),
    ("red spider severe", "Red Spider", "High"),
    ("tea leaf curl high", "Blister Blight", "High"),
    ("rust orange patches medium", "Red Rust", "Medium"),
    ("blister high", "Blister Blight", "High"),
    ("grey blite low", "Grey Blight", "Low"),
    ("brown spot medium", None, None),
    ("pesticide recommendation", None, None),
    ("tea fertilizer high", None, None),
    ("coffee rust high", None, None),
    ("thaveesha urvinda", None, None)
]



