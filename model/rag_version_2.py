import csv
import logging
import os
from datetime import datetime
import chromadb
import ollama
import pandas as pd
from sentence_transformers import SentenceTransformer

# Lowest confidence = 53.7
# Logger configuration
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

class TeaDiseaseRAG:
    def __init__(self, excel_path, db_path, embedding_model = 'BAAI/bge-small-en-v1.5'):
        self.excel_path = excel_path
        self.db_path = db_path
        self.embedding_model_name = embedding_model

        # Initialize
        self.embedder = SentenceTransformer(self.embedding_model_name)
        self.client = chromadb.PersistentClient(path = self.db_path)
        self.collection = self.client.get_or_create_collection(name = "treatments_data")

        # Auto ingest if empty
        if self.collection.count() == 0:
            self.ingest_data()
        else:
            logging.info(f"Database loaded with {self.collection.count()} records.")


    def ingest_data(self):
        # Reads excel and create the ChromaDB collection.
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

            # Strong disease name and severity for perfect matching
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


    def get_recommendation(self, disease_name, severity_level, location = "Sri Lanka"):
        query = f"{disease_name} {severity_level}"
        query_embedding = self.embedder.encode(query).tolist()
        severity_cap = severity_level.capitalize()
        logging.info(f"Querying for: {disease_name} ({severity_cap})")

        # Search with metadata filter (with strong severity match)
        results = self.collection.query(
            query_embeddings = [query_embedding],
            n_results = 1,
            where = {"severity": severity_cap},
            include = ["metadatas", "distances"]
        )

        # Fallback if no exact severity match
        if not results['ids'] or not results['ids'][0]:
            logging.warning(f"No match for severity '{severity_cap}'. Searching...")
            results = self.collection.query(
                query_embeddings = [query_embedding],
                n_results = 1,
                include = ["metadatas", "distances"]
            )

        if not results['ids'] or not results['ids'][0]:
            return {"status": "Error occurred", "message": "No matching data found."}

        # Get the best match
        best_match = None
        best_index = 0

        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            match = results["metadatas"][0][i]
            confidence = round((1 - distance) * 100, 1)

            if severity_level.lower() in match["severity"].lower():
                best_match = match
                best_index = i
                break

        if not best_match:
            best_match = results["metadatas"][0][0]
            best_index = 0

        disease = best_match["disease"]
        severity = best_match["severity"]
        symptoms = best_match["symptoms"]
        treatments = best_match["treatments"]
        confidence_percent = round((1 - results["distances"][0][best_index]) * 100, 1)

        # If low confidence
        if confidence_percent < 50:
            print(f"\nLow confidence match detected ({confidence_percent}%)")

            # Show top 3
            all_results = self.collection.query(
                query_embeddings = [query_embedding],
                n_results = 3,
                include = ["metadatas"]
            )

            print("System is not very confident about this match.")
            print("Following are some matches")
            for i, meta in enumerate(all_results["metadatas"][0]):
                print(f"{i + 1} . {meta['disease']} - {meta['severity']} severity")

            print("\nPlease try again and enter a correct query.")

            return {
                "status": "low_confidence",
                "message": "Low confidence match. Please enter a correct query."
            }

        # Generate LLM Response
        llm_prompt = f"""
        You are a helpful tea disease assistant in {location}, Sri Lanka. Mention the provided location in the response.
        Only use the provided information below. Do not add, invent, or assume any facts.

        Retrieved data:
        Disease: {disease}
        Severity: {severity}
        Symptoms: {symptoms}
        Treatments: {treatments}

        Give a friendly, simple response in English.
        - Explain symptoms in easy words in point form
        - List and explain treatments in bullet points and give respective percentages
        - Add 2-3 practical tips for local farmers
        - Keep short (150-250 words)
        - End with safety note
        """

        try:
            ollama_response = ollama.chat(model = 'llama3.1:8b', messages = [
                {'role': 'user', 'content': llm_prompt}
            ])
            final_response = ollama_response['message']['content'].strip()
        except Exception as e:
            final_response = f"Error generating ollama response: {str(e)}"

        # Log and return
        self.log_request(query, severity, location, disease, confidence_percent, final_response)
        print(f"Confidence: {confidence_percent}%")

        return {
            "status": "success",
            "matched_disease": disease,
            "matched_severity": severity,
            "llm_response": final_response,
            "confidence": confidence_percent
        }


    def log_request(self, query, severity, location, disease, confidence, response):
        file_exists = os.path.isfile("rag_log.csv")
        with open("rag_log.csv", "a", newline = '', encoding = 'utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Query", "Severity", "Location", "Disease", "Confidence", "Response"])
            writer.writerow([datetime.now(), query, severity, location, disease, confidence, response])


    def get_treatment(self, disease_name, severity_level, location = "Sri Lanka"):
        respond = self.get_recommendation(disease_name, severity_level, location = "Sri Lanka")
        response = (respond.get("llm_response"), respond.get("confidence"))
        return response


# Main
if __name__ == "__main__":
    # System initialization
    rag_system = TeaDiseaseRAG(
        excel_path = "../data_folder/treatments_data_v2.xlsx",
        db_path = "chroma_DB"
    )

    # Run an example query
    result = rag_system.get_recommendation(
        disease_name = "Blister Blight",
        severity_level = "Honda",
        location = "Hatton"
    )

    print("\nLLM response:")
    print(result.get('llm_response', result.get('message')))


