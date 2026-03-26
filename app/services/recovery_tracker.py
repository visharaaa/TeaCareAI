import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model

from config import Config


class TreatmentProgressTracker:

    def __init__(self,model_path='recovery_model.h5', scaler_path='scaler.pkl', feature_cols_path='feature_columns.pkl'):
        self.model        = load_model(model_path, compile=False)
        self.scaler       = joblib.load(scaler_path)
        self.feature_cols = joblib.load(feature_cols_path)

    # Private helper method (underscore means it's for internal use only)
    # Take the six input features and return a single recovery score
    # This is called twice inside check_progress(): once for day 0 and one for the current state
    def _get_score(self, disease, days_after_treatment, initial_affected_area_pct,
                   affected_area_pct, color_deviation, humidity):

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

        # One-hot encoding the diseases
        input_dict[f'disease_{disease}'] = 1

        # Converts dict. into a single row dataframe
        input_df     = pd.DataFrame([input_dict])[self.feature_cols]
        input_scaled = self.scaler.transform(input_df)

        # Making the prediction
        score        = self.model.predict(input_scaled, verbose=0)[0][0] * 100

        return round(float(np.clip(score, 0, 100)), 1)

    # Main public method the system calls
    def check_progress(self, disease, initial_affected_area_pct, days_after_treatment,
                       affected_area_pct, color_deviation, humidity):

        # Score at day 0: how the leaf looked when treatment was first applied
        initial_score = self._get_score(
            disease, 0, initial_affected_area_pct,
            initial_affected_area_pct, color_deviation, humidity
        )

        # Score now: how the leaf looks today
        current_score = self._get_score(
            disease, days_after_treatment, initial_affected_area_pct,
            affected_area_pct, color_deviation, humidity
        )

        # Treatment effectiveness = how much has changed since day 0
        # Positive change means it has improved, negative means otherwise
        #The ±2 threshold filters out tiny fluctuations that are within the model's margin of error before labelling something as improving or deteriorating.
        change = current_score - initial_score

        if change > 2:
            formated_output = f"Improving (+{change:.1f}%)"
            status="improving"
        elif change < -2:
            formated_output = f"Deteriorating ({change:.1f}%)"
            status="deteriorating"
        else:
            formated_output = "Stable (0.0%)"
            status="stable"

        # Print progress report
        # print("\n--- Treatment Progress Report ---")
        # print(f"  Disease             : {disease.replace('_', ' ').title()}")
        # print(f"  Days Since Treatment: {days_after_treatment}")
        # print(f"  Score at Day 0      : {initial_score}%")
        # print(f"  Current Score       : {current_score}%")
        # print(f"  Treatment Effect    : {formated_output}")

        result={
            'current_score' : current_score,
            'change' : change,
            'status' : status,
            'formated_output' : formated_output
        }

        # Returns the three values
        return result

#
# # Example
#
# if __name__ == "__main__":
#
#     tracker = TreatmentProgressTracker(
#         model_path=Config.NN_MODEL_PATH,
#         scaler_path=Config.NN_SCALER_PATH,
#         feature_cols_path=Config.NN_FEATURE_COLUMNS_PATH
#     )
#
#     print(tracker.check_progress(
#         disease='brown_blight',
#         initial_affected_area_pct=40.0,   # from database back when the leaf was first scanned
#         days_after_treatment=14,           # get from user
#         affected_area_pct=60.0,            # from current uploaded image
#         color_deviation=0.25,              # from current uploaded image
#         humidity=70.0                      # current reading
#     ))