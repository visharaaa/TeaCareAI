import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import os
import ollama
import json
from datetime import datetime
import csv
import logging

# Logger configuration
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

class TeaDiseaseRAG:
    def __init__(self, excel_path, db_path, embedding_model = 'BAAI/bge-small-en-v1.5'):
        self.excel_path = excel_path
        self.db_path = db_path
        self.embedding_model_name = embedding_model

        # Initialize resources
        self.embedder = SentenceTransformer(self.embedding_model_name)
        self.client = chromadb.PersistentClient(path = self.db_path)
        self.collection = self.client.get_or_create_collection(name = "treatments_data")





