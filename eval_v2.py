import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from tensorflow.keras.models import load_model

# Load saved model and test data
model = load_model('recovery_model.h5', compile=False)
model.compile(optimizer='adam', loss='mse', metrics=['mae'])
data      = joblib.load('test_data.pkl')
X_test    = data['X_test']
y_test    = data['y_test'] * 100.0   # rescale back to 0–100
history   = data['history']

# Predict
y_pred = model.predict(X_test).flatten() * 100.0

# Metrics
mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)

print("── Evaluation Results ──────────────────")
print(f"  MAE  (avg error in score points) : {mae:.2f}")
print(f"  RMSE                             : {rmse:.2f}")
print(f"  R²   (variance explained)        : {r2:.4f}")
print("────────────────────────────────────────")

# Plots
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
fig.suptitle('Tea Leaf Recovery Model — Evaluation', fontsize=13, fontweight='bold')

# Loss curve
axes[0].plot(history['loss'],     label='Train',      color='#2E7D32', linewidth=2)
axes[0].plot(history['val_loss'], label='Validation', color='#FF6F00', linewidth=2, linestyle='--')
axes[0].set_title('Loss (MSE) over Epochs')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('MSE')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Predicted vs Actual
axes[1].scatter(y_test, y_pred, alpha=0.4, color='#1565C0', s=25)
axes[1].plot([0, 100], [0, 100], 'r--', linewidth=1.5, label='Perfect')
axes[1].set_title(f'Predicted vs Actual\nR² = {r2:.4f}  |  MAE = {mae:.2f}')
axes[1].set_xlabel('Actual Score')
axes[1].set_ylabel('Predicted Score')
axes[1].legend()
axes[1].grid(alpha=0.3)

# Residuals
residuals = y_pred - y_test
axes[2].hist(residuals, bins=25, color='#6A1B9A', edgecolor='white', alpha=0.8)
axes[2].axvline(0, color='red', linestyle='--', linewidth=1.5)
axes[2].set_title('Residuals Distribution')
axes[2].set_xlabel('Predicted − Actual')
axes[2].set_ylabel('Count')
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('evaluation_plots.png', dpi=150, bbox_inches='tight')
plt.show()
print("\nPlot saved as evaluation_plots.png")
