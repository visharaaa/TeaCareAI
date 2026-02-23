import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# Load model
model = load_model("tea_health_model.h5", compile=False)

# Load scaler + feature structure
scaler = joblib.load("scaler.pkl")
feature_columns = joblib.load("feature_columns.pkl")

# Create new sample (example)
df_new = pd.DataFrame({
    "Total_Leaf_Area_mm2": [1500],
    "Affected_Area_Pre": [300],
    "Humidity_Pct": [85],
    "Temp_Celsius": [28],
    "Disease_Type": ["Red Rust"]
})

# One-hot encode like training
df_new = pd.get_dummies(df_new, columns=["Disease_Type"])

# Force same structure as training
df_new = df_new.reindex(columns=feature_columns, fill_value=0)

# Scale
new_leaf_scaled = scaler.transform(df_new)

# Predict
prediction = model.predict(new_leaf_scaled)

print("Predicted Health Improvement %:", prediction[0][0])
