import numpy as np
import pandas as pd
import joblib # to load the saved scaler and feature columns
from tensorflow.keras.models import load_model # to load the trained neural network


class TreatmentProgressTracker:

    # Load the three saved files from training ->
    # the neural network model, scaler which was fitted on the training data, and the feature column order

    def __init__(self,model_path='recovery_model.h5',scaler_path='recovery_scaler.sav',feature_cols_path='feature_columns.pkl'):
        self.model        = load_model(model_path, compile=False)
        self.scaler       = joblib.load(scaler_path)
        self.feature_cols = joblib.load(feature_cols_path)

    # Define the inputs that are accepted by the method. six features are used here.

    def predict_recovery(self, disease, days_after_treatment, initial_affected_area_pct,
                         affected_area_pct, color_deviation, humidity):

    # Build a dictionary of all the 10 input features expected by the model.
    # Disease labels are set to 0 by default and will be flipped to 1 in the next step according to disease that was passed in

        input_dict = {
            'days_after_treatment':      days_after_treatment,
            'initial_affected_area_pct': initial_affected_area_pct,
            'affected_area_pct':         affected_area_pct,
            'color_deviation':           color_deviation,
            'humidity':                  humidity,
            'disease_blister_blight':    0,
            'disease_brown_blight':      0,
            'disease_grey_blight':       0,
            'disease_helopeltis':        0,
            'disease_red_rust':          0,
        }

        # One-hot encode the disease -> Set the correct disease column to 1
        input_dict[f'disease_{disease}'] = 1

        # Converts the dictionary into a single-row dataframe
        # Reorders columns to match how the training data was structured
        input_df     = pd.DataFrame([input_dict])[self.feature_cols]
        input_scaled = self.scaler.transform(input_df)

        # Passes the scaled input through the NN and gets the predicted recovery score
        # Multiplies it by 100 to convert from the 0-1 training scale back to 0-100
        score        = self.model.predict(input_scaled, verbose=0)[0][0] * 100

        # To make sure score doesn't go above 100 or below 0 and is rounded to 1 decimal place
        score        = round(float(np.clip(score, 0, 100)), 1)

        # Recovery status label specifications
        if score >= 70:   status = "good_recovery"
        elif score >= 40: status = "moderate_recovery"
        else:             status = "poor_recovery"

        if (initial_affected_area_pct-affected_area_pct)<0:
            status = "escalated"
            score = (initial_affected_area_pct-initial_affected_area_pct)*(-1)



        # # Print report
        # print("\n--- Leaf Health Progress ---")
        # print(f"  Disease        : {disease.replace('_', ' ').title()}")
        # print(f"  Day            : {days_after_treatment}")
        # print(f"  Recovery Score : {score}%")
        # print(f"  Status         : {status}")
        # print("----------------------------\n")

        return score, status


# Example usage
#
# if __name__ == "__main__":
#
#     tracker = TreatmentProgressTracker()
#
#     tracker.predict_recovery(
#         disease='brown_blight',
#         days_after_treatment=3,
#         initial_affected_area_pct=40.0,
#         affected_area_pct=32.0,
#         color_deviation=0.12, # Color deviation has to be between 0 and 1
#         humidity=70.0
#     )