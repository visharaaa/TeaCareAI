import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model

# Load saved model, scaler, and feature columns
model        = load_model('recovery_model.h5', compile=False)
scaler       = joblib.load('scaler.pkl')
feature_cols = joblib.load('feature_columns.pkl')


def predict_recovery(disease, days_after_treatment, initial_affected_area_pct,
                     affected_area_pct, lesion_count, lesion_avg_size_mm2,
                     color_deviation, humidity, treatment_effectiveness):

    input_dict = {
        'days_after_treatment':      days_after_treatment,
        'initial_affected_area_pct': initial_affected_area_pct,
        'affected_area_pct':         affected_area_pct,
        'lesion_count':              lesion_count,
        'lesion_avg_size_mm2':       lesion_avg_size_mm2,
        'color_deviation':           color_deviation,
        'humidity':                  humidity,
        'treatment_effectiveness':   treatment_effectiveness,
        'disease_blister_blight':    0,
        'disease_brown_blight':      0,
        'disease_grey_blight':       0,
        'disease_helopeltis':        0,
        'disease_red_rust':          0,
    }

    input_dict[f'disease_{disease}'] = 1
    input_df     = pd.DataFrame([input_dict])[feature_cols]
    input_scaled = scaler.transform(input_df)
    score        = model.predict(input_scaled, verbose=0)[0][0] * 100

    return round(float(np.clip(score, 0, 100)), 1)


def health_change(before_score, after_score):
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

    # Score at day 0 (just before/after treatment applied)
    before = predict_recovery(
        disease='grey_blight',
        days_after_treatment=0,
        initial_affected_area_pct=50.0,
        affected_area_pct=50.0,
        lesion_count=11,
        lesion_avg_size_mm2=4.2,
        color_deviation=0.80,
        humidity=70.0,
        treatment_effectiveness=1.0
    )

    # Score at day 14 (after treatment)
    after = predict_recovery(
        disease='grey_blight',
        days_after_treatment=14,
        initial_affected_area_pct=50.0,
        affected_area_pct=6.0,
        lesion_count=2,
        lesion_avg_size_mm2=1.1,
        color_deviation=0.12,
        humidity=70.0,
        treatment_effectiveness=1.0
    )

    health_change(before, after)