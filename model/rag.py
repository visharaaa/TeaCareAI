import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import os
import sys

# Define paths
treatments_file = "../data_folder/treatments_data_v2.xlsx"
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

# Loop through each row in the data frame
for index, row in df.iterrows():
    # Check if the disease column has a value
    if pd.notna(row["Disease"]):
        disease = row["Disease"]
    else:
        disease = "Unknown disease"

    # Check if the severity column has a value
    if "Severity" in df.columns and pd.notna(row["Severity"]):
        severity = row["Severity"]
    else:
        severity = "Unknown severity"

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

    # Save row as a complete new entry
    data.append({
        "disease": disease,
        "severity": severity,
        "symptoms": symptom,
        "treatments": treatment
    })

print(f"{len(data)} rows loaded\n")

# Manually embedding the data
documents = []
embeddings = []
metadatas = []
ids = []

for entry in data:
    # Strong disease name and severity for perfect matching
    text_for_embedding = (
        f"Severity level: {entry['severity']} {entry['severity']} {entry['severity']} {entry['severity']} {entry['severity']} "
        f"High severity is critical, medium is moderate, low is mild - "
        f"Current entry is {entry['severity']} severity for {entry['disease']} {entry['disease']} "
        f"Symptoms: {entry['symptoms']} Treatments: {entry['treatments']}"
    )

    documents.append(text_for_embedding)
    embeddings.append(embedder.encode(text_for_embedding).tolist()) # Manual embedding

    metadatas.append({
        "disease": entry["disease"],
        "severity": entry["severity"],
        "symptoms": entry["symptoms"],
        "treatments": entry["treatments"]
    })

    # Make ID unique per disease and severity
    ids.append(f"{entry['disease'].lower().replace(' ', '_')}_{entry['severity'].lower().replace(' ', '_')}")

# Chroma DB setup
client = chromadb.PersistentClient(path = database_folder)
collection = client.get_or_create_collection(name ="treatments_data")

if collection.count() == 0:
    collection.add(
        documents = documents,
        embeddings = embeddings, # Providing embeddings manually
        metadatas = metadatas,
        ids = ids
    )
    print("Data and embeddings added to the database successfully")
else:
    print("Database already has data")

# Query setup
query = "blister blight high"

print(f"Searching for '{query}'")
print("Please wait...")

# Embedding the query
query_embedding = embedder.encode(query).tolist()

# Search in the database
results = collection.query(
    query_embeddings = [query_embedding],
    n_results = 1,
    include = ["distances", "metadatas"] # Distance for confidence check
)

# Checking if found results
if results["ids"] and results["ids"][0]:
    distance = results["distances"][0][0] # Lowest distance gives better match

    # Confidence threshold
    if distance < 0.92:
        match = results["metadatas"][0][0]
        disease_name = match["disease"]
        severity = match["severity"]
        symptoms = match["symptoms"]
        treatments = match["treatments"]
        confidence_percent = round((1 - distance) * 100, 1)

        # Outputting results
        print(f"Match found: {disease_name}")
        print(f"Severity level: {severity}")
        print(f"Confidence: {confidence_percent}%")
        print("=" * 60)

        print("You may wee symptoms like:")
        print("-" * 50)
        if symptoms.strip():
            print(symptoms)
        else:
            print("No symptoms recorded")

        print(f"\nRecommended treatments for {disease_name} ({severity} severity):")
        print("-" * 50)
        print(treatments)
        print("\nNote: Always consult a local agricultural expert before applying treatments")
    else:
        # Not enough confidence (low confidence)
        print("\nNo confident match found.")
        print(f"\nMatching distance is too low = {distance:.3f}")
        print("Available diseases:\n")
        for entry in data:
            print(f"{entry['disease']}")
else:
    # No match at all
    print("No match found for the query")
    print("Available diseases:")
    for entry in data:
        print(f"{entry['disease']}")





