import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Load dataset
df = pd.read_excel("smart_home_energy_consumption_large.xlsx")

df.columns = df.columns.str.strip()

df['timestamp'] = pd.to_datetime(
    df[['Year', 'Month', 'Day', 'Hour', 'Minute']]
)

df.rename(columns={
    'Energy Consumption (kWh)': 'energy'
}, inplace=True)

df = df.sort_values('timestamp')

# Scale energy
scaler = MinMaxScaler()
df['scaled_energy'] = scaler.fit_transform(df[['energy']])

# Save scaler
joblib.dump(scaler, "scaler.pkl")

# Create sequences
def create_sequences(data, seq_len=24):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i:i+seq_len])
        y.append(data[i+seq_len])
    return np.array(X), np.array(y)

series = df['scaled_energy'].values
X, y = create_sequences(series)

# Split
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Build LSTM
model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(24,1)),
    LSTM(32),
    Dense(1)
])

model.compile(optimizer='adam', loss='mse')

# Train
model.fit(X_train.reshape(-1,24,1), y_train, epochs=5, batch_size=32)

# Save model
model.save("energy_lstm_model.h5")

print("Model and scaler saved successfully!")
