import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

app = Flask(__name__)

PRICE_PER_KWH = 8

# ======================================================
# LOAD DATA
# ======================================================
df = pd.read_excel("smart_home_energy_consumption_large.xlsx")
df.columns = df.columns.str.strip()
df.rename(columns={'Energy Consumption (kWh)': 'energy'}, inplace=True)

df['timestamp'] = pd.to_datetime(
    df['Date'].astype(str) + " " + df['Time'].astype(str),
    errors='coerce'
)

df = df.dropna(subset=['timestamp'])
df = df.sort_values("timestamp")

df['hour'] = df['timestamp'].dt.hour

# ======================================================
# LOAD LSTM MODEL
# ======================================================
model = load_model("energy_lstm_model.keras")
scaler = joblib.load("scaler.pkl")

df['scaled_energy'] = scaler.transform(df[['energy']].values)

# ======================================================
# DASHBOARD ROUTE
# ======================================================
@app.route("/", methods=["GET", "POST"])
def dashboard():

    current_usage = float(df['energy'].iloc[-1])

    # LSTM next hour prediction
    if len(df) >= 24:
        last_24 = df['scaled_energy'].values[-24:]
        input_seq = last_24.reshape(1, 24, 1)
        pred_scaled = model.predict(input_seq, verbose=0)
        next_hour_pred = scaler.inverse_transform(pred_scaled)[0][0]
    else:
        next_hour_pred = current_usage

    current_cost = round(current_usage * PRICE_PER_KWH, 2)
    predicted_cost = round(next_hour_pred * PRICE_PER_KWH, 2)

    trend = df['energy'].tail(48).tolist()

    # ======================================================
    # MONTHLY DEVICE AGGREGATION
    # ======================================================
    df['year'] = df['timestamp'].dt.year
    df['month'] = df['timestamp'].dt.month

    latest_year = df['year'].max()
    latest_month = df[df['year'] == latest_year]['month'].max()

    monthly_data = df[
        (df['year'] == latest_year) &
        (df['month'] == latest_month)
    ]

    if monthly_data.empty:
        device_data = pd.Series(dtype=float)
    else:
        device_data = monthly_data.groupby('Appliance Type')['energy'].sum().sort_values(ascending=False)

    devices = device_data.index.tolist()
    values = device_data.values.tolist()

    total_units = device_data.sum() if not device_data.empty else 0
    current_bill = round(total_units * PRICE_PER_KWH, 2)

    predicted_month_bill = None

    if request.method == "POST" and not device_data.empty:
        selected_devices = request.form.getlist("devices")
        if selected_devices:
            new_units = device_data[selected_devices].sum()
            predicted_month_bill = round(new_units * PRICE_PER_KWH, 2)

    # ======================================================
    # ADVANCED SMART SUGGESTIONS
    # ======================================================
    suggestions = []

    historical_mean = df['energy'].mean()

    if current_usage > historical_mean * 1.2:
        suggestions.append("⚠ Current usage is significantly above average.")

    if not device_data.empty:
        top_device = device_data.idxmax()
        suggestions.append(f"🔌 {top_device} is the highest energy consuming device this month.")

    peak_usage = df[(df['hour'] >= 18) & (df['hour'] <= 22)]['energy'].mean()
    non_peak_usage = df[(df['hour'] < 18) | (df['hour'] > 22)]['energy'].mean()

    if peak_usage > non_peak_usage:
        suggestions.append("⏰ High peak-hour consumption detected (6PM–10PM).")

    potential_saving = round(total_units * 0.1 * PRICE_PER_KWH, 2)
    suggestions.append(f"💰 Potential savings: ₹ {potential_saving} if optimized.")

    if next_hour_pred > historical_mean * 1.2:
        suggestions.append("🔮 Predicted next-hour usage is high.")

    if not suggestions:
        suggestions.append("✅ Energy consumption is stable.")

    return render_template(
        "dashboard.html",
        current_usage=round(current_usage, 2),
        next_hour_pred=round(next_hour_pred, 2),
        current_cost=current_cost,
        predicted_cost=predicted_cost,
        trend=trend,
        devices=devices,
        values=values,
        current_bill=current_bill,
        predicted_month_bill=predicted_month_bill,
        suggestions=suggestions
    )


if __name__ == "__main__":
    app.run(debug=True)