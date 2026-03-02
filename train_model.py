import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import joblib

# Load Dataset
df = pd.read_excel('data/tea_health_dataset.xlsx')
print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# Preprocessing
# Convert categorical Disease_Type to numeric
df = pd.get_dummies(df, columns=['Disease_Type'])

# Features and target
X = df.drop(columns=['Health_Improvement_Pct', 'Affected_Area_Post'])
X = X.select_dtypes(include=[np.number])  # only numeric
y = df['Health_Improvement_Pct']


# Split and Scale
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Building the Neural Network
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(1)  # Output: Health Improvement %
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])
print(f"Training started with {X_train_scaled.shape[1]} features...")


# Training
history = model.fit(
    X_train_scaled, y_train,
    epochs=100,
    batch_size=10,
    validation_split=0.1,
    verbose=1
)


# Save Model, Scaler, and Features
model.save('tea_health_model.h5')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(X_train.columns, 'feature_columns.pkl')
print("✅ Model, scaler, and feature columns saved.")