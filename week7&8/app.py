#import libraries
from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import os
import joblib
from tensorflow.keras.models import load_model

app = Flask(__name__)

# CONFIG 
DATA_PATH = "smart_home_time.csv"
MODEL_DIR = "models"
TARGET_COL = "Energy Consumption (kWh)"
TIME_STEPS = 24

# LOAD DATA 
df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
df = df.set_index("timestamp").sort_index()

# HOME 
@app.route("/")
def home():
    return render_template("index.html")

# APPLIANCES 
@app.route("/api/appliances")
def appliances():
    devices = sorted(df["Appliance Type"].dropna().unique())
    return jsonify({"appliances": devices})

# OVERALL 
@app.route("/api/overall")
def overall():
    period = request.args.get("period", "daily")
    base = df.groupby(df.index)[TARGET_COL].sum()

    if period == "hourly":
        series = base
        labels = [i.strftime("%Y-%m-%d %H:%M") for i in series.index]
    elif period == "daily":
        series = base.resample("D").sum()
        labels = [i.strftime("%Y-%m-%d") for i in series.index]
    elif period == "monthly":
        series = base.resample("MS").sum()
        labels = [i.strftime("%b %Y") for i in series.index]
    else:
        return jsonify({"error": "Invalid period"}), 400

    return jsonify({"labels": labels, "values": series.tolist()})

# DEVICE 
@app.route("/api/device")
def device_chart():
    device = request.args.get("device")
    period = request.args.get("period", "daily")

    df_app = df[df["Appliance Type"] == device]
    base = df_app.groupby(df_app.index)[TARGET_COL].sum()

    if period == "hourly":
        series = base
        labels = [i.strftime("%Y-%m-%d %H:%M") for i in series.index]
    elif period == "daily":
        series = base.resample("D").sum()
        labels = [i.strftime("%Y-%m-%d") for i in series.index]
    elif period == "monthly":
        series = base.resample("MS").sum()
        labels = [i.strftime("%b %Y") for i in series.index]
    else:
        return jsonify({"error": "Invalid period"}), 400

    return jsonify({"labels": labels, "values": series.tolist()})

# DEVICE TOTALS (for pie chart - actual historical consumption)
@app.route("/api/device_totals")
def device_totals():
    totals = df.groupby("Appliance Type")[TARGET_COL].sum()
    return jsonify(totals.to_dict())

# DEVICE STATS (mean + std for smart prediction thresholds)
@app.route("/api/device_stats")
def device_stats():
    stats = df.groupby("Appliance Type")[TARGET_COL].agg(["mean", "std"]).fillna(0)
    result = {
        device: {
            "mean": row["mean"],
            "std":  row["std"]
        }
        for device, row in stats.iterrows()
    }
    return jsonify(result)

# SINGLE PREDICTION 
@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json()
    device = data["device"]

    safe = device.replace(" ", "_")
    model_path = f"{MODEL_DIR}/lstm_{safe}.h5"
    scaler_path = f"{MODEL_DIR}/scaler_{safe}.pkl"

    model = load_model(model_path, compile=False)
    scaler = joblib.load(scaler_path)

    df_device = df[df["Appliance Type"] == device]
    values = df_device[TARGET_COL].values.reshape(-1, 1)

    scaled = scaler.transform(values)
    last_24 = scaled[-24:]
    X = np.reshape(last_24, (1, TIME_STEPS, 1))

    pred_scaled = model.predict(X, verbose=0)
    pred = scaler.inverse_transform(pred_scaled)

    return jsonify({
        "device": device,
        "prediction": float(pred[0][0])
    })

# ALL PREDICTIONS 
@app.route("/api/predict_all")
def predict_all():
    predictions = {}
    appliances = df["Appliance Type"].unique()

    for device in appliances:
        safe = device.replace(" ", "_")
        model_path = f"{MODEL_DIR}/lstm_{safe}.h5"
        scaler_path = f"{MODEL_DIR}/scaler_{safe}.pkl"

        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            continue

        model = load_model(model_path, compile=False)
        scaler = joblib.load(scaler_path)

        df_app = df[df["Appliance Type"] == device].sort_index()
        if len(df_app) < TIME_STEPS:
            continue

        values = df_app[TARGET_COL].values.reshape(-1, 1)
        scaled = scaler.transform(values)
        last_24 = scaled[-TIME_STEPS:]
        X = np.reshape(last_24, (1, TIME_STEPS, 1))

        pred_scaled = model.predict(X, verbose=0)
        pred = scaler.inverse_transform(pred_scaled)

        predictions[device] = float(pred[0][0])

    return jsonify(predictions)

# INSIGHTS 
@app.route("/api/insights")
def insights():
    summary = df.groupby("Appliance Type")[TARGET_COL].sum()

    highest_device = summary.idxmax()
    highest_value = summary.max()
    lowest_device = summary.idxmin()
    lowest_value = summary.min()

    return jsonify({
        "highest_device": highest_device,
        "highest_value": float(highest_value),
        "lowest_device": lowest_device,
        "lowest_value": float(lowest_value)
    })

if __name__ == "__main__":
    app.run(debug=True)