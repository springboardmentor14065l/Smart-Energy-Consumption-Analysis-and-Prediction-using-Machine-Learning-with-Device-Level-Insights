import os
import numpy as np
import pandas as pd
import joblib

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam

DATA_PATH = "dataset/smart_home_time.csv"
MODEL_DIR = "models"
TIME_STEPS = 24

os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
df = df.set_index("timestamp")

appliances = df["Appliance Type"].unique()

def create_sequences(data, time_steps):
    X, y = [], []
    for i in range(time_steps, len(data)):
        X.append(data[i-time_steps:i])
        y.append(data[i])
    return np.array(X), np.array(y)

for appliance in appliances:

    print(f"\nTraining LSTM for: {appliance}")

    df_app = df[df["Appliance Type"] == appliance].copy()
    df_app = df_app.sort_index()

    values = df_app["Energy Consumption (kWh)"].values.reshape(-1,1)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    X, y = create_sequences(scaled, TIME_STEPS)

    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(TIME_STEPS,1)),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(1)
    ])

    model.compile(optimizer=Adam(0.001), loss="mse")

    early_stop = EarlyStopping(
        monitor="val_loss",
        patience=5,
        restore_best_weights=True
    )

    model.fit(
        X_train, y_train,
        epochs=30,
        batch_size=32,
        validation_split=0.1,
        callbacks=[early_stop],
        verbose=1
    )

    y_pred = model.predict(X_test)

    y_test_inv = scaler.inverse_transform(y_test)
    y_pred_inv = scaler.inverse_transform(y_pred)

    mae = mean_absolute_error(y_test_inv, y_pred_inv)
    rmse = np.sqrt(mean_squared_error(y_test_inv, y_pred_inv))

    print("MAE:", mae)
    print("RMSE:", rmse)

    safe = appliance.replace(" ", "_")

    model.save(f"{MODEL_DIR}/lstm_{safe}.h5")
    joblib.dump(scaler, f"{MODEL_DIR}/scaler_{safe}.pkl")

print("\n✅ All appliance LSTMs trained successfully.")
