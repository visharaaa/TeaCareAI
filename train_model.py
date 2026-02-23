from threading import activeCount
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import joblib

# Load the data
df = pd.read_excel('data/health_tracker_dataset.xlsx')

# Turning Disease_Type to numbers
df = pd.get_dummies(df, columns=['Disease_Type'])

# Define input X and target y
X = df.drop(columns=['Health_Improvement_Pct', 'Affected_Area_Post'], errors = 'ignore')
X = X.select_dtypes(include=[np.number])
y = df['Health_Improvement_Pct']

# Split data into Training (80%) and Testing (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=42)

# Scaling the data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Building the NN
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(1) # Output should be the predicted % change
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Training the model
print(f"Training started with {X_train_scaled.shape[1]} features (including Days)...")
history = model.fit(X_train_scaled, y_train, epochs=100, batch_size=10, validation_split=0.1)

model.save ('tea_health_model.h5')
print("Model has been saved as tea_health_model.h5")


joblib.dump(scaler, "scaler.pkl")
joblib.dump(X_train.columns, "feature_columns.pkl")
