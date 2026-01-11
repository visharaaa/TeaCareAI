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





