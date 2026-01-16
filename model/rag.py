import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import os
import sys

# Define paths
treatments_file = "../data_folder/treatments_data.xlsx"
database_folder = "chroma_DB"

# Print paths for debugging
print("Project folder:", os.getcwd())
print("Database folder:", os.path.join(os.getcwd(), database_folder))
print("Excel file:", os.path.join(os.getcwd(), treatments_file))

# Load the embedding model
print("Loading the embedding model...")
embedder = SentenceTransformer('all-MiniLM-L6-v2')
print("Embedding model loaded successfully")

# Read the excel file
df = pd.read_excel(treatments_file)
print("Number of columns in the excel file:", list(df.columns))
print("-" * 50)

# Identify the treatments column
treatment_col = None
for col in df.columns:
    if "treatment" in str(col).lower():
        treatment_col = col
        break
print("Treatment column:", treatment_col)

if treatment_col is None:
    print("Error: No treatment column found")
    sys.exit()

print(f"Using treatments column: '{treatment_col}'")

# Organizing data to embed
data = []
current_disease = None
current_symptoms = []
current_treatments = []

# Loop through each row in the data frame
for index, row in df.iterrows():
    # Check if the disease column has a value
    if pd.notna(row["Disease"]):
        disease = row["Disease"]
    else:
        disease = None

    # Check if the symptoms column has a value
    if pd.notna(row["Detailed Symptoms"]):
        symptom = row["Detailed Symptoms"]
    else:
        symptom = ""

    # Check if the treatment column has a value
    if pd.notna(row[treatment_col]):
        treatment = row[treatment_col]
    else:
        treatment = ""

    # Checking if a new disease name is found
    if disease:
        # If already collecting data for previous disease
        if current_disease is not None:
            data.append({
                "disease": current_disease,
                "symptoms": "\n".join(current_symptoms),
                "treatments": "\n".join(current_treatments)
            })

        # Start tracking the new disease
        current_disease = disease

        # Reset the symptom list
        current_symptoms = []
        if symptom:
            current_symptoms.append(symptom)

        # Reset the treatment list
        current_treatments = []
        if treatment:
            current_treatments.append(treatment)

    # If no new disease
    else:
        # Add rest of the symptoms
        if symptom:
            current_symptoms.append(symptom)

        # Add rest of the treatments
        if treatment:
            current_treatments.append(treatment)


# To save last disease after finishing all rows
if current_disease is not None:
    data.append({
        "disease": current_disease,
        "symptoms": "\n".join(current_symptoms),
        "treatments": "\n".join(current_treatments)
    })

print(f"{len(data)} diseases loaded\n")

# Manually embedding the data
documents = []
embeddings = []
metadatas = []
ids = []

for entry in data:
    # Strong disease name for perfect matching
    text_for_embedding = f"{entry["disease"]} {entry["disease"]} {entry["disease"]} - Treatments for {entry["disease"]}: {entry["treatments"]}"

    documents.append(text_for_embedding)
    embeddings.append(embedder.encode(text_for_embedding).tolist()) # Manual embedding

    metadatas.append({
        "disease": entry["disease"],
        "treatments": entry["treatments"],
        "symptoms": entry["symptoms"]
    })

    ids.append(entry["disease"].lower().replace(" ", "_"))





