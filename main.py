import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model


class TreatmentProgressTracker:

    def __init__(self):
        self.model        = load_model('recovery_model.h5', compile=False)
        self.scaler       = joblib.load('scaler.pkl')
        self.feature_cols = joblib.load('feature_columns.pkl')

    def predict_recovery(self, disease, days_after_treatment, initial_affected_area_pct,
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

        input_dict[f'disease_{disease}'] = 1
        input_df     = pd.DataFrame([input_dict])[self.feature_cols]
        input_scaled = self.scaler.transform(input_df)
        score        = self.model.predict(input_scaled, verbose=0)[0][0] * 100

        return round(float(np.clip(score, 0, 100)), 1)

    def health_change(self, before_score, after_score):
        change = after_score - before_score

        if change > 2:
            trend = "Improving"
        elif change < -2:
            trend = "Deteriorating"
        else:
            trend = "Stable"

        print("\n--- Leaf Health Progress ---")
        print(f"  Before Treatment : {before_score} / 100")
        print(f"  After Treatment  : {after_score} / 100")
        print(f"  Health Change    : {change:+.1f}%")
        print(f"  Status           : {trend}")
        print("----------------------------\n")

        return change, trend


# ── Example usage ────────────────────────────

if __name__ == "__main__":

    tracker = TreatmentProgressTracker()

    before = tracker.predict_recovery(
        disease='grey_blight',
        days_after_treatment=0,
        initial_affected_area_pct=50.0,
        affected_area_pct=50.0,
        color_deviation=0.80,
        humidity=70.0
    )

    after = tracker.predict_recovery(
        disease='grey_blight',
        days_after_treatment=14,
        initial_affected_area_pct=50.0,
        affected_area_pct=6.0,
        color_deviation=0.12,
        humidity=70.0
    )

    tracker.health_change(before, after)