import pandas as pd
import numpy as np

np.random.seed(42)


def generate_tea_data(rows=1000):
    diseases = ['blister blight', 'brown blight', 'grey blight', 'red rust', 'helopeltis']
    data = []

    for i in range(rows):
        disease = np.random.choice(diseases)

        # 1. Initial Leaf Condition
        leaf_area = np.random.uniform(500, 1500)
        affected_area_pre = leaf_area * np.random.uniform(0.2, 0.7)

        # 2. Environmental Factors
        humidity = np.random.uniform(60, 95)
        temp = np.random.uniform(20, 35)

        # 3. Base Effectiveness by Disease Type
        disease_effectiveness = {
            'blister blight': 0.75,
            'brown blight': 0.70,
            'grey blight': 0.68,
            'red rust': 0.65,
            'helopeltis': 0.60  # insect pest → slightly harder to control
        }

        base_effectiveness = disease_effectiveness[disease]

        # 4. Environmental Influence

        # Fungal diseases worsen in high humidity
        if 'blight' in disease or disease == 'red rust':
            humidity_penalty = (humidity - 70) * 0.008
            base_effectiveness -= humidity_penalty

        # Helopeltis (insect pest) increases with higher temperature
        if disease == 'helopeltis':
            temp_penalty_insect = (temp - 25) * 0.012
            base_effectiveness -= temp_penalty_insect

        # General temperature stress for all
        temp_penalty = (temp - 25) * 0.01
        base_effectiveness -= temp_penalty

        # 5. Small Biological Variance
        recovery_factor = base_effectiveness + np.random.normal(0, 0.03)
        recovery_factor = np.clip(recovery_factor, 0.1, 0.95)

        # 6. After Treatment
        affected_area_post = affected_area_pre * (1 - recovery_factor)

        # 7. Health Improvement %
        health_improvement = recovery_factor * 100

        data.append([
            disease,
            round(leaf_area, 2),
            round(affected_area_pre, 2),
            round(affected_area_post, 2),
            round(humidity, 1),
            round(temp, 1),
            round(health_improvement, 2)
        ])

    columns = [
        'disease_type',
        'total_leaf_area_mm2',
        'affected_area_pre',
        'affected_area_post',
        'humidity_pct',
        'temp_celsius',
        'health_improvement_pct'
    ]

    return pd.DataFrame(data, columns=columns)


df = generate_tea_data(1000)
df.to_excel('tea_health_tracker.xlsx', index=False)

print("Dataset generated successfully.")
