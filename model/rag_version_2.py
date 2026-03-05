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

        # Auto-ingest if empty
        if self.collection.count() == 0:
            self.ingest_data()
        else:
            logging.info(f"Database loaded with {self.collection.count()} records.")

    def ingest_data(self):
        # Reads Excel and create the ChromaDB collection.
        if not os.path.exists(self.excel_path):
            logging.error(f"Excel file not found at {self.excel_path}")
            return

        logging.info("Reading Excel file and generating embeddings...")
        df = pd.read_excel(self.excel_path)

        # Find treatment column dynamically
        treatment_col = None
        for col in df.columns:
            if "treatment" in str(col).lower():
                treatment_col = col
                break
        print("Treatment column:", treatment_col)

        if treatment_col is None:
            logging.error("No 'treatment' column was found in Excel file.")
            return

        documents = []
        embeddings = []
        metadatas = []
        ids = []

        for index, row in df.iterrows():
            if row.isna().all():
                continue

            disease = str(row.get("Disease", "Unknown"))
            severity = str(row.get("Severity", "Unknown")).strip()
            symptoms = str(row.get("Detailed Symptoms", "")).strip()
            treatment = str(row.get(treatment_col, "")).strip()

            # Strong disease name and severity for perfect matching (your original version)
            text_for_embedding = (
                f"Severity level: {severity} {severity} {severity} {severity} {severity} "
                f"High severity is critical, medium is moderate, low is mild - "
                f"Current entry is {severity} severity for {disease} {disease} "
                f"Symptoms: {symptoms} Treatments: {treatment}"
            )

            documents.append(text_for_embedding)
            embeddings.append(self.embedder.encode(text_for_embedding).tolist())

            metadatas.append({
                "disease": disease,
                "severity": severity,
                "symptoms": symptoms,
                "treatments": treatment
            })

            clean_id = f"{disease}_{severity}".lower().replace(" ", "_")
            ids.append(clean_id)

        # Batch add to ChromaDB
        if documents:
            self.collection.add(
                documents = documents,
                embeddings = embeddings,
                metadatas = metadatas,
                ids = ids
            )
            logging.info(f"Successfully ingested {len(documents)} records.")
