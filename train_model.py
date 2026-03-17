import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# Load data
# Read CSV into a dataframe and one-hot encode disease column (turn single text column to 5 binary columns)
df = pd.read_csv('data/tea_leaf_recovery_v3.csv')
df = pd.get_dummies(df, columns=['disease'], prefix='disease')

# X contains all the input features -> all except the target variable
# y contains the target variable recovery_score
# recovery score is divided by 100 to scale it from 0-1
X = df.drop(columns=['recovery_score'])
y = df['recovery_score'] / 100.0  # scale to 0–1

# Split and scale
# Split into 800 and 200 for training and testing
# random_state ensure split is same every time script is run
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# StandardScales rescales all features to have mean = 0 and SD = 1
# fit_transform is called on training data only
# transform is applied to test data using the same scale learnt from training
# Never fitting on test data to avoid data leakage
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# Build model
# Final layer ->  1 neuron with linear activation
# because this is a regression task outputting a single continuous value
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(1,  activation='linear')
])

model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])

# Monitors validation loss during training and stops automatically if it doesn't improve for 15 consecutive epochs
early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)

# Trains model on scaled training data
# validation_split= reserves 15% of the training data to monitor performance on unseen data during training
history = model.fit(
    X_train_scaled, y_train,
    validation_split=0.15,
    epochs=100, # max. no. of training cycles
    batch_size=32,
    callbacks=[early_stop],
    verbose=1
)

# Save
model.save('recovery_model.h5') # Trained NN
joblib.dump(scaler, 'scaler.pkl') # Fitted scaler for new inputs to be scaled the same way
joblib.dump(list(X.columns), 'feature_columns.pkl') # Saves column order for inputs to always be fed in the correct order
joblib.dump({'X_test': X_test_scaled, 'y_test': y_test.values, 'history': history.history}, 'test_data.pkl') # Saves test set and training history

print("\nSaved: recovery_model.h5, scaler.pkl, feature_columns.pkl, test_data.pkl")
