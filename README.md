# 🍵 Tea Disease Treatment Recommendation RAG

**Component 2** of the Tea Leaf Disease Detection, Treatment Recommendation and Recovery Tracking System.  
**Developed for:** BSc (Hons) in AI & Data Science  

---

## 🌟 Overview

This is a **Retrieval-Augmented Generation (RAG)** system designed to provide accurate, severity-specific treatment recommendations for common tea leaf diseases in Sri Lanka. 

By taking a **disease name and severity level** as input, the system returns:
- **Matched Disease & Severity:** High-precision metadata filtering.
- **Detailed Symptoms:** Specific indicators for the identified stage.
- **Multi-Modal Treatments:** Cultural, chemical, and biocontrol options.
- **Farmer-Friendly Explanations:** Natural language responses generated locally by Ollama.

### 🚀 Key Highlights
- **94.4% Retriever Accuracy:** Reliable data fetching from the knowledge base.
- **0.893 Faithfulness Score:** Ensures LLM responses stay true to the provided facts.
- **100% Offline:** Operates entirely without internet using local vector stores and models.
- **Safety First:** Includes a low-confidence clarification feature (prevents answers when confidence < 50%).
- **Integration Ready:** Optimized for API or component-based integration with JSON output.

---

## ✨ Features

- **Metadata Filtering:** Ensures 100% accurate matching for Disease + Severity combinations.
- **Local Intelligence:** Uses Ollama (Llama 3.1) for human-like reasoning without cloud dependency.
- **Robust Output:** Supports both natural language for farmers and structured JSON for developers.
- **Full Traceability:** Automatically logs every query, result, and evaluation metric to CSV and JSON.
- **Clean Architecture:** Modular class-based design using the `TeaDiseaseRAG` class.

---
