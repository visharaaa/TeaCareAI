import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model

# Load saved model, scaler, and feature columns
model = load_model('recovery_model.h5', compile=False)
model.compile(optimizer='adam', loss='mse', metrics=['mae'])
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

    disease_key = f'disease_{disease}'
    if disease_key not in input_dict:
        raise ValueError(f"Unknown disease '{disease}'. Choose from: "
                         "blister_blight, brown_blight, grey_blight, helopeltis, red_rust")

    input_dict[disease_key] = 1

    input_df     = pd.DataFrame([input_dict])[feature_cols]
    input_scaled = scaler.transform(input_df)
    score        = model.predict(input_scaled, verbose=0)[0][0] * 100

    return round(float(np.clip(score, 0, 100)), 1)


# ── Test cases ───────────────────────────────

tests = [
    {
        'label': 'Grey blight — Day 14, mostly healed',
        'inputs': dict(disease='grey_blight', days_after_treatment=14,
                       initial_affected_area_pct=50.0, affected_area_pct=6.0,
                       lesion_count=2, lesion_avg_size_mm2=1.1,
                       color_deviation=0.12, humidity=65.0, treatment_effectiveness=1.1)
    },
    {
        'label': 'Red rust — Day 7, still progressing',
        'inputs': dict(disease='red_rust', days_after_treatment=7,
                       initial_affected_area_pct=45.0, affected_area_pct=28.0,
                       lesion_count=7, lesion_avg_size_mm2=3.2,
                       color_deviation=0.70, humidity=82.0, treatment_effectiveness=0.9)
    },
    {
        'label': 'Blister blight — Day 0, just treated',
        'inputs': dict(disease='blister_blight', days_after_treatment=0,
                       initial_affected_area_pct=65.0, affected_area_pct=65.0,
                       lesion_count=14, lesion_avg_size_mm2=4.5,
                       color_deviation=0.88, humidity=78.0, treatment_effectiveness=1.0)
    },
    {
        'label': 'Helopeltis — Day 21, scarring stage',
        'inputs': dict(disease='helopeltis', days_after_treatment=21,
                       initial_affected_area_pct=40.0, affected_area_pct=18.0,
                       lesion_count=15, lesion_avg_size_mm2=1.8,
                       color_deviation=0.18, humidity=70.0, treatment_effectiveness=1.05)
    },
]

print("── Sample Predictions ───────────────────")
for test in tests:
    score = predict_recovery(**test['inputs'])
    print(f"\n  {test['label']}")
    print(f"  → Recovery Score: {score} / 100")
print("\n─────────────────────────────────────────")