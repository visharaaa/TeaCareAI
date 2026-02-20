import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import os
import sys
import ollama
import json
from datetime import datetime
import csv

# Define paths
treatments_file = "../data_folder/treatments_data_v2.xlsx"
database_folder = "chroma_DB"

# Print paths for debugging
print("Project folder:", os.getcwd())
print("Database folder:", os.path.join(os.getcwd(), database_folder))
print("Excel file:", os.path.join(os.getcwd(), treatments_file))

# Load the embedding model
print("Loading the embedding model...")
# embedder = SentenceTransformer('all-MiniLM-L6-v2')
embedder = SentenceTransformer('BAAI/bge-small-en-v1.5')
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
    # Skip empty rows completely
    if row.isna().all():
        continue

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

# Query setup with JSON
json_file = "../data_folder/input.json"
try:
    with open(json_file, 'r', encoding = 'utf-8') as f:
        input_data = json.load(f)

    disease_name = input_data.get("disease_name", "").strip().lower()
    severity_level = input_data.get("severity_level", "").strip().lower()
    location = input_data.get("location", "Sri Lanka").strip()

    if not disease_name or not severity_level:
        print("Error: Missing 'disease_name' or 'severity_level' in JSON.")
        sys.exit()

    # Create the query from JSON
    query = f"{disease_name} {severity_level}"

except FileNotFoundError:
    print(f"Error: JSON file not found at {json_file}")
    sys.exit()
except json.JSONDecodeError:
    print("Error: Invalid JSON format.")
    sys.exit()
except Exception as e:
    print(f"Error while reading JSON: {e}")
    sys.exit()

print(f"Searching for '{query}' (location: {location})")
print("Please wait...")

# Embedding the query
query_embedding = embedder.encode(query).tolist()

# Find an exact severity match
severity_cap = severity_level.capitalize()

filtered_results = collection.query(
    query_embeddings = [query_embedding],
    n_results = 1,
    where = { "severity": severity_cap}, # To get the exact severity
    include = ["distances", "metadatas"]
)

# Use filtered if found otherwise fallback to unfiltered
if filtered_results["ids"] and filtered_results["ids"][0]:
    results = filtered_results
    print(f"Found exact severity match: {severity_cap}")
else:
    print(f"No exact {severity_cap} match... falling back to best overall match")
    # Search in the database
    results = collection.query(
        query_embeddings = [query_embedding],
        n_results = 1,
        include = ["distances", "metadatas"] # Distance for confidence check
    )

# Checking if found results
if results["ids"] and results["ids"][0]:
    print(f"Found {len(results['ids'][0])} possible matches:")
    print("=" * 60)

    best_match = None
    best_index = 0

    # Prefer the one where severity matches user request
    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i] # Lowest distance gives better match
        match = results["metadatas"][0][i]
        confidence = round((1 - distance) * 100, 1)
        print(f"Match {i + 1}: {match['disease']} ({match['severity']}) - Confidence: {confidence}%")

        # Boost if severity matches user input
        if severity_level.lower() in match["severity"].lower():
            best_match = match
            best_index = i
            break

    # Fallback to the best match if no severity match
    if not best_match:
        best_match = results["metadatas"][0][0]
        best_index = 0

    disease_name = best_match["disease"]
    severity = best_match["severity"]
    symptoms = best_match["symptoms"]
    treatments = best_match["treatments"]
    confidence_percent = round((1 - results["distances"][0][best_index]) * 100, 1)

    # Ollama response
    llm_prompt = f"""
    You are a helpful tea disease assistant in {location}, Sri Lanka. Mention the provided location in the response since the user lives there.
    Only use the provided information below. Do not add, invent, or assume any facts.

    Retrieved data:
    Disease: {disease_name}
    Severity: {severity}
    Symptoms: {symptoms}
    Treatments: {treatments}

    Give a friendly, simple response in English.
    - Explain symptoms in easy words in point form
    - List and explain treatments in bullet points
    - Add 2-3 practical tips for local farmers
    - Keep short (150-250 words)
    - End with safety note
    """

    # Call Ollama (llama3.1:8b model)
    ollama_response = ollama.chat(model = 'llama3.1:8b', messages = [{
        'role': 'user',
        'content': llm_prompt,
    }])

    final_response = ollama_response['message']['content'].strip()

    # Outputting results
    print(f"Best match: {disease_name}")
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

    # Ollama response
    print("\nOllama output:")
    print("-" * 50)
    print("\n" + final_response)

    # JSON output file
    output_json = {
        "query": query,
        "location": location,
        "matched_disease": disease_name,
        "matched_severity": severity,
        "confidence_percent": confidence_percent,
        "symptoms": symptoms.strip() if symptoms.strip() else "No symptoms recorded",
        "treatments": treatments,
        "llm_response": final_response,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "success"
    }

    # Save to JSON file
    json_output_file = "output.json"
    with open(json_output_file, "w", encoding = "utf-8") as f:
        json.dump(output_json, f, indent = 4, ensure_ascii = False)

    print(f"JSON output saved to {json_output_file}")

    # Logging the information
    log_file = "rag_log.csv"
    headers = ["Query", "Location", "Matched Disease", "Matched Severity", "Confidence (%)", "LLM Response", "Timestamp"]

    file_exists = os.path.isfile(log_file)

    with open(log_file, "a", newline = "", encoding = "utf-8") as f:
        writer = csv.writer(f)
        if not file_exists or os.stat(log_file).st_size == 0:
            writer.writerow(headers)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([query, location, disease_name, severity, confidence_percent, final_response, timestamp])
    print(f"Information logged to {log_file}")

else:
    # No match at all
    print("No match found for the query")
    print("Available diseases:")
    for entry in data:
        print(f"{entry['disease']}")





