# retriever_correctness.py

from sentence_transformers import SentenceTransformer
import chromadb
from sklearn.metrics import precision_score, recall_score, f1_score

embedder = SentenceTransformer('BAAI/bge-small-en-v1.5')
client = chromadb.PersistentClient(path = "chroma_DB")
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

# Finding correct answers
y_pred = []
y_true = []
for test_case in test_cases:
    first_value = test_case[0]
    disease_label = test_case[1]
    third_value = test_case[2]
    if disease_label is not None:
        y_true.append(1) # match
    else:
        y_true.append(0) # do not match

# Testing by looping through test cases
for query, expected_disease, expected_severity in test_cases:
    query_embedding = embedder.encode(query).tolist()
    # Get the severity level from last word
    if " " in query:
        words = query.split()
        severity_level = words[-1]
    else:
        severity_level = "medium"
    severity_cap = severity_level.capitalize()

    # Find best match for severity level
    filtered = collection.query(
        query_embeddings = [query_embedding],
        n_results = 1,
        where = {"severity": severity_cap},
        include = ["metadatas"]
    )

    if filtered["ids"] and filtered["ids"][0]: # If match found, save it
        match = filtered["metadatas"][0][0]
    else: # Else find best match without severity level
        unfiltered = collection.query(
            query_embeddings = [query_embedding],
            n_results = 1,
            include = ["metadatas"]
        )
        if unfiltered["ids"]:
            match = unfiltered["metadatas"][0][0]
        else: # Nothing found
            match = None

    correct = 0
    if match is not None:
        if match["disease"] == expected_disease:
            if match["severity"] == expected_severity:
                correct = 1
            else:
                correct = 0
        else:
            correct = 0
    else:
        correct = 0
    y_pred.append(correct)

# Evaluation metrics
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)

correct_count = 0
for i in range(len(y_true)):
    if y_true[i] == y_pred[i]:
        correct_count = correct_count + 1
    else:
        pass
accuracy = (correct_count / len(y_true)) * 100

print("Retriever Correctness Evaluation (no threshold):")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1-Score: {f1:.4f}")
print(f"Accuracy: {accuracy:.1f}%")
print(f"Test queries: {len(test_cases)}")


