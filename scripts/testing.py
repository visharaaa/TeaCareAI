import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                             r2_score, classification_report, confusion_matrix)
from tensorflow.keras.models import load_model

# Load saved model and test data
model  = load_model('recovery_model.h5', compile=False)
data   = joblib.load('test_data.pkl')
X_test = data['X_test']
y_test = data['y_test'] * 100.0
y_pred = model.predict(X_test).flatten() * 100.0

# Regression Metrics
mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)

print("── Regression Metrics ───────────────────────")
print(f"  MAE  : {mae:.2f}")
print(f"  RMSE : {rmse:.2f}")
print(f"  R²   : {r2:.4f}")
print("─────────────────────────────────────────────\n")

# Convert scores to 3 stage labels
def score_to_stage(score):
    if score >= 70:   return "Good Recovery"
    elif score >= 40: return "Moderate Recovery"
    else:             return "Poor Recovery"

stage_order   = ["Poor Recovery", "Moderate Recovery", "Good Recovery"]
y_test_labels = [score_to_stage(s) for s in y_test]
y_pred_labels = [score_to_stage(s) for s in y_pred]

# Classification Report
print("── Classification Report ─────────────────────")
print(classification_report(y_test_labels, y_pred_labels,
                             labels=stage_order, zero_division=0))

# Confusion Matrix
cm = confusion_matrix(y_test_labels, y_pred_labels, labels=stage_order)

fig, ax = plt.subplots(figsize=(7, 5))
fig.suptitle('Tea Leaf Recovery Model: Testing Report', fontsize=13, fontweight='bold')

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=stage_order, yticklabels=stage_order, ax=ax)
ax.set_title('Confusion Matrix')
ax.set_xlabel('Predicted Stage')
ax.set_ylabel('Actual Stage')

plt.tight_layout()
plt.savefig('testing_report.png', dpi=150, bbox_inches='tight')
plt.show()
print("\nPlot saved as testing_report.png")