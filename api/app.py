from flask_cors import CORS
from flask import Flask, request, jsonify
from predictor import load_model_and_scaler, predict_next
import pandas as pd

app = Flask(__name__)
CORS(app)

DATA_PATH = "../data/processed/hourly_device_energy.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])

COMPARISON_PATH = "../outputs/module5_model_comparison.csv"


@app.route("/")
def home():
    return "Energy Prediction API Running 🚀"


# ---------------- PREDICTION ----------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    appliance = data["appliance"]

    appliance_df = df[df["Appliance Type"] == appliance].sort_values("timestamp")

    last_24 = appliance_df.tail(24)["Energy Consumption (kWh)"].values

    model, scaler = load_model_and_scaler(appliance)
    prediction = predict_next(model, scaler, last_24)

    return jsonify({
        "next_hour_prediction_kWh": float(prediction)
    })


# ---------------- HISTORICAL SUMMARY ----------------
@app.route("/historical", methods=["POST"])
def historical():
    data = request.get_json()
    appliance = data["appliance"]

    appliance_df = df[df["Appliance Type"] == appliance].sort_values("timestamp")
    latest_time = appliance_df["timestamp"].max()

    last_24h = appliance_df[appliance_df["timestamp"] >= latest_time - pd.Timedelta(hours=24)]
    last_7d = appliance_df[appliance_df["timestamp"] >= latest_time - pd.Timedelta(days=7)]
    last_30d = appliance_df[appliance_df["timestamp"] >= latest_time - pd.Timedelta(days=30)]

    return jsonify({
        "hourly_total": float(last_24h["Energy Consumption (kWh)"].sum()),
        "weekly_total": float(last_7d["Energy Consumption (kWh)"].sum()),
        "monthly_total": float(last_30d["Energy Consumption (kWh)"].sum())
    })


# ---------------- SMART SUGGESTIONS ----------------
@app.route("/suggestions", methods=["POST"])
def suggestions():
    data = request.get_json()
    appliance = data["appliance"]

    appliance_df = df[df["Appliance Type"] == appliance].sort_values("timestamp")
    latest_time = appliance_df["timestamp"].max()
    last_7d = appliance_df[appliance_df["timestamp"] >= latest_time - pd.Timedelta(days=7)]

    weekly_total = last_7d["Energy Consumption (kWh)"].sum()

    suggestions = []

    if weekly_total > 500:
        suggestions = [
            f"{appliance} usage is very high this week.",
            "Reduce operating hours during peak periods.",
            "Inspect appliance efficiency or maintenance status."
        ]
    elif weekly_total > 250:
        suggestions = [
            f"{appliance} has moderate energy usage.",
            "Monitor peak consumption times.",
            "Use eco or energy-saving modes."
        ]
    else:
        suggestions = [
            f"{appliance} usage is energy efficient.",
            "Maintain balanced usage patterns.",
            "No optimization required currently."
        ]

    return jsonify({"suggestions": suggestions})


# ---------------- ANALYTICS ----------------
@app.route("/analytics", methods=["POST"])
def analytics():
    data = request.get_json()
    appliance = data["appliance"]

    appliance_df = df[df["Appliance Type"] == appliance].sort_values("timestamp")

    hourly = appliance_df.tail(24)

    daily = appliance_df.set_index("timestamp").resample("D").sum().tail(30)
    weekly = appliance_df.set_index("timestamp").resample("W").sum().tail(12)
    monthly = appliance_df.set_index("timestamp").resample("M").sum().tail(12)

    return jsonify({
        "hourly_labels": hourly["timestamp"].dt.strftime("%H:%M").tolist(),
        "hourly_values": hourly["Energy Consumption (kWh)"].tolist(),

        "daily_labels": daily.index.strftime("%Y-%m-%d").tolist(),
        "daily_values": daily["Energy Consumption (kWh)"].tolist(),

        "weekly_labels": weekly.index.strftime("Week %U").tolist(),
        "weekly_values": weekly["Energy Consumption (kWh)"].tolist(),

        "monthly_labels": monthly.index.strftime("%Y-%m").tolist(),
        "monthly_values": monthly["Energy Consumption (kWh)"].tolist()
    })


# ---------------- MODEL COMPARISON ----------------
@app.route("/model_comparison", methods=["POST"])
def model_comparison():
    data = request.get_json()
    appliance = data["appliance"]

    comparison_df = pd.read_csv(COMPARISON_PATH)

    row = comparison_df[comparison_df["Appliance"] == appliance]

    if row.empty:
        return jsonify({"error": "No data found"}), 404

    lr_mae = float(row["LR_MAE"].values[0])
    lstm_mae = float(row["LSTM_MAE"].values[0])

    best_model = "LSTM" if lstm_mae < lr_mae else "Linear Regression"

    return jsonify({
        "lr_mae": lr_mae,
        "lstm_mae": lstm_mae,
        "best_model": best_model
    })


if __name__ == "__main__":
    app.run(debug=True)