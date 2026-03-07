import pandas as pd
import numpy as np
import joblib
import tensorflow as tf


class LeafEvaluator:
    def __init__(self, model_path='tea_health_model.h5', scaler_path='scaler.pkl', feature_path='feature_columns.pkl'):
        self.model = tf.keras.models.load_model(model_path, compile=False)
        self.scaler = joblib.load(scaler_path)
        self.feature_columns = joblib.load(feature_path)

    def predict_improvement(self, leaf_input: dict):
        """
        leaf_input: dictionary with keys as feature names, e.g.,
        {
            'Total_Leaf_Area_mm2': 1200,
            'Affected_Area_Pre': 350,
            'Humidity_Pct': 78,
            'Temp_Celsius': 26,
            'Disease_Type_Blister Blight': 1,
            'Disease_Type_Brown Blight': 0,
            ...
        }
        """
        # Convert dict to DataFrame with correct column order
        df = pd.DataFrame([leaf_input], columns=self.feature_columns)
        X_scaled = self.scaler.transform(df)

        pred = self.model.predict(X_scaled, verbose=0)[0][0]
        return round(pred, 2)

"""if __name__ == "__main__":
        evaluator = LeafEvaluator()

        leaf_input = {
            'Total_Leaf_Area_mm2': 1200,
            'Affected_Area_Pre': 400,
            'Affected_Area_Post': 120,
            'Humidity_Pct': 75,
            'Temp_Celsius': 27,
            'Disease_Type_Blister Blight': 1,
            'Disease_Type_Brown Blight': 0,
            'Disease_Type_Grey Blight': 0,
            'Disease_Type_Red Rust': 0,
            'Disease_Type_Red Spider': 0
        }

        prediction = evaluator.predict_improvement(leaf_input)
        print(f"Predicted Health Improvement: {prediction:.2f}%")
"""