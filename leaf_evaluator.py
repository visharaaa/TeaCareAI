import numpy as np
import pandas as pd
import tensorflow as tf
import joblib

# Load trained components
model = tf.keras.models.load_model("tea_health_model.h5", compile = False)
scaler = joblib.load("scaler.pkl")
feature_columns = joblib.load("feature_columns.pkl")



# Calculate actual improvement
def calculate_improvement(pre_area, post_area):
    if pre_area == 0:
        return 0
    improvement = ((pre_area - post_area) / pre_area) * 100
    return round(improvement, 2)


# Function to predict using NN
def predict_improvement(input_data_dict):

    # Convert to DataFrame
    input_df = pd.DataFrame([input_data_dict])

    # One-hot encoding for Disease_Type
    input_df = pd.get_dummies(input_df)

    # Ensure all training columns exist
    for col in feature_columns:
        if col not in input_df.columns:
            input_df[col] = 0

    # Reorder columns to match training
    input_df = input_df[feature_columns]

    # Scale
    input_scaled = scaler.transform(input_df)

    # Predict
    prediction = model.predict(input_scaled)

    return round(float(prediction[0][0]), 2)


# Example
if __name__ == "__main__":

    # Example input
    leaf_data = {
        "Total_Leaf_Area_mm2": 1200,
        "Affected_Area_Pre": 400,
        "Humidity_Pct": 78,
        "Temp_Celsius": 26,
        "Disease_Type_Red Rust": 1,
        "Disease_Type_Red Spider": 0,
        "Disease_Type_Grey Blight": 0,
        "Disease_Type_Blister Blight": 0,
        "Disease_Type_Brown Blight": 0
    }

    actual_improvement = calculate_improvement(
        pre_area=400,
        post_area=150
    )

    predicted_improvement = predict_improvement(leaf_data)

    print("Actual Improvement:", actual_improvement, "%")
    print("Predicted Improvement (NN):", predicted_improvement, "%")

    if actual_improvement > 0:
        print("Leaf condition improved.")
    elif actual_improvement < 0:
        print("Leaf condition deteriorated.")
    else:
        print("No change detected.")