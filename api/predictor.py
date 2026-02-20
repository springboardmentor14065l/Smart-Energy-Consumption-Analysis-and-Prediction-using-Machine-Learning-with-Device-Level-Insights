import numpy as np
import joblib
from tensorflow.keras.models import load_model

def load_model_and_scaler(appliance):

    model_path = f"../models/lstm_energy_model_{appliance.replace(' ', '_')}.keras"
    scaler_path = f"../models/scaler_{appliance.replace(' ', '_')}.pkl"

    model = load_model(model_path)
    scaler = joblib.load(scaler_path)

    return model, scaler


def predict_next(model, scaler, last_values):

    # Convert to numpy
    last_values = np.array(last_values).reshape(-1, 1)

    # Scale
    scaled = scaler.transform(last_values)

    # Reshape for LSTM (1 sample, 24 timesteps, 1 feature)
    scaled = scaled.reshape(1, 24, 1)

    # Predict
    pred_scaled = model.predict(scaled)

    # Inverse scale
    pred = scaler.inverse_transform(pred_scaled)

    return float(pred[0][0])
