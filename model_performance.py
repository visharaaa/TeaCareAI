import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


# Load dataset
df = pd.read_excel('data/tea_health_dataset.xlsx')

# Apply same encoding
df = pd.get_dummies(df, columns=['Disease_Type'])

# Load saved feature order
feature_columns = joblib.load("feature_columns.pkl")

# Select same features
X = df[feature_columns]
y = df['Health_Improvement_Pct']

# Same split as training
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Load scaler and model
scaler = joblib.load("scaler.pkl")
model = tf.keras.models.load_model("tea_health_model.h5", compile=False)

# Scale test set
X_test_scaled = scaler.transform(X_test)

# Predict
predictions = model.predict(X_test_scaled, verbose=0).flatten()

# Metrics
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

residuals = y_test - predictions
within_5 = np.mean(np.abs(residuals) <= 5) * 100
within_10 = np.mean(np.abs(residuals) <= 10) * 100

print("\nMODEL PERFORMANCE REPORT")
print("------------------------------------------------")
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"R² Score: {r2:.3f}")
print(f"Predictions within ±5% error: {within_5:.2f}%")
print(f"Predictions within ±10% error: {within_10:.2f}%")

# Visualization
plt.figure()
plt.scatter(y_test, predictions)
plt.plot([0, 100], [0, 100])
plt.xlabel("Actual Improvement (%)")
plt.ylabel("Predicted Improvement (%)")
plt.title("Actual vs Predicted Improvement")
plt.show()