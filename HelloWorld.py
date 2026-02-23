import pandas as pd
df = pd.read_excel('data/health_tracker_dataset.xlsx')
df = pd.get_dummies(df, columns=['Disease_Type'])
# This prints the EXACT names you need to copy
print(df.drop(columns=['Health_Improvement_Pct', 'Affected_Area_Post', 'Timestamp'], errors='ignore').columns.tolist())