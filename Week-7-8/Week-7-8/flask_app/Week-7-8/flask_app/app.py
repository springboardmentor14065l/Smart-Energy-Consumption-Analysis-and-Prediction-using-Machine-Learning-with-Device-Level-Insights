"""
Smart Energy Monitor — app.py
Flask REST API Backend
Milestone 4 — Week 7-8
"""

import os
import json
import pickle
import zipfile
import threading
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════

APPLIANCES = [
    "Air Conditioning", "Computer", "Dishwasher", "Fridge",
    "Heater", "Lights", "Microwave", "Oven", "TV", "Washing Machine"
]
SEQ_LENGTH = 24       # 24 hours of history for LSTM input
MODELS_DIR = "lstm_models"

# ═══════════════════════════════════════════════════════════════════
# FLASK APP
# ═══════════════════════════════════════════════════════════════════

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Global storage (loaded once at startup)
models           = {}   # { appliance_name: keras_model }
scalers          = {}   # { appliance_name: MinMaxScaler }
app_data         = {}   # { appliance_name: np.array of kWh values }
app_stats_cache  = {}   # { appliance_name: dict of stats + chart data }


# ═══════════════════════════════════════════════════════════════════
# STARTUP: Load Models, Scalers, Data
# ═══════════════════════════════════════════════════════════════════

def load_everything():
    """
    Called once when Flask starts.
    Loads LSTM models, scalers, CSV data, computes all stats.
    """
    global models, scalers, app_data, app_stats_cache

    # ── Try to import TensorFlow ───────────────────────────────────
    tf_available = False
    try:
        import tensorflow as tf
        from tensorflow.keras.models import load_model as keras_load
        tf_available = True
        print(f"[STARTUP] TensorFlow {tf.__version__} loaded")
    except ImportError:
        print("[STARTUP] TensorFlow not found — using statistical fallback")

    # ── Extract lstm_models.zip if present ─────────────────────────
    if os.path.exists("lstm_models.zip") and not os.path.isdir(MODELS_DIR):
        print("[STARTUP] Extracting lstm_models.zip...")
        with zipfile.ZipFile("lstm_models.zip", "r") as z:
            z.extractall(MODELS_DIR)
        print(f"[STARTUP] Extracted to ./{MODELS_DIR}/")

    # ── Load CSV data ──────────────────────────────────────────────
    if os.path.exists("processed_hourly_energy.csv"):
        df = pd.read_csv("processed_hourly_energy.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        print(f"[STARTUP] Loaded CSV: {df.shape}")
    else:
        print("[STARTUP] CSV not found — generating synthetic demo data")
        df = _generate_demo_data()

    # ── Load models + scalers + compute stats per appliance ────────
    for appliance in APPLIANCES:
        app_clean = appliance.replace(" ", "_").replace("/", "_")
        app_df    = df[df["Appliance Type"] == appliance].sort_values("timestamp")
        vals      = app_df["Energy Consumption (kWh)"].values
        app_data[appliance] = vals

        # Load or fit scaler
        scaler_path = os.path.join(MODELS_DIR, f"scaler_{app_clean}.pkl")
        if os.path.exists(scaler_path):
            with open(scaler_path, "rb") as f:
                scalers[appliance] = pickle.load(f)
        else:
            sc = MinMaxScaler()
            sc.fit(vals.reshape(-1, 1))
            scalers[appliance] = sc

        # Load LSTM model
        if tf_available:
            for ext in [".h5", ".keras", ""]:
                model_path = os.path.join(MODELS_DIR, f"lstm_{app_clean}{ext}")
                if os.path.exists(model_path):
                    try:
                        models[appliance] = keras_load(model_path)
                        print(f"[STARTUP]   ✓ Model loaded: {appliance}")
                        break
                    except Exception as e:
                        print(f"[STARTUP]   ⚠ Could not load {model_path}: {e}")

        # Compute evaluation metrics (on last 200 points)
        preds, actuals = [], []
        for i in range(SEQ_LENGTH, min(len(vals), SEQ_LENGTH + 200)):
            hist = list(vals[i - SEQ_LENGTH:i])
            preds.append(predict_next(appliance, hist))
            actuals.append(vals[i])

        preds   = np.array(preds)
        actuals = np.array(actuals)

        mae  = float(mean_absolute_error(actuals, preds))
        rmse = float(np.sqrt(mean_squared_error(actuals, preds)))
        r2   = float(r2_score(actuals, preds))
        r2   = max(-1.0, min(1.0, r2))  # clamp

        # Chart data: last 7 days actual vs predicted
        recent      = app_df.tail(7 * 24)
        timestamps  = recent["timestamp"].dt.strftime("%Y-%m-%d %H:%M").tolist()
        actual_vals = recent["Energy Consumption (kWh)"].tolist()

        pred_vals = []
        all_vals  = app_df["Energy Consumption (kWh)"].values
        start_idx = len(all_vals) - 7 * 24
        for i in range(7 * 24):
            idx = start_idx + i
            if idx >= SEQ_LENGTH:
                pred_vals.append(predict_next(appliance, list(all_vals[idx - SEQ_LENGTH:idx])))
            else:
                pred_vals.append(actual_vals[i] if i < len(actual_vals) else 0.0)

        # Daily totals (last 14 days)
        daily_df  = app_df.copy()
        daily_df["date"] = daily_df["timestamp"].dt.date
        daily_sum = daily_df.groupby("date")["Energy Consumption (kWh)"].sum().tail(14)

        # Hourly average pattern
        hourly_avg = (
            app_df.groupby(app_df["timestamp"].dt.hour)["Energy Consumption (kWh)"]
            .mean().round(3).tolist()
        )

        app_stats_cache[appliance] = {
            "mae":       round(mae, 3),
            "rmse":      round(rmse, 3),
            "r2":        round(r2, 3),
            "total_kwh": round(float(vals.sum()), 2),
            "avg_kwh":   round(float(vals.mean()), 3),
            "max_kwh":   round(float(vals.max()), 3),
            "min_kwh":   round(float(vals.min()), 3),
            "has_model": appliance in models,
            # Chart data
            "timestamps":   timestamps,
            "actual_vals":  [round(float(v), 3) for v in actual_vals],
            "pred_vals":    [round(float(v), 3) for v in pred_vals],
            "hourly_avg":   hourly_avg,
            "daily_labels": [str(d) for d in daily_sum.index.tolist()],
            "daily_vals":   [round(float(v), 2) for v in daily_sum.values.tolist()],
        }

    print(f"[STARTUP] Done — {len(models)} LSTM models, {len(scalers)} scalers ready")
    print(f"[STARTUP] Appliances loaded: {list(app_stats_cache.keys())}")


def _generate_demo_data():
    """Generate 1 year of synthetic energy data when CSV is missing."""
    np.random.seed(42)
    base_usage = {
        "Air Conditioning": 8.0, "Computer": 3.0,  "Dishwasher": 2.0,
        "Fridge": 1.5,           "Heater":   7.0,  "Lights":     1.0,
        "Microwave": 0.5,        "Oven":     2.5,  "TV":         1.2,
        "Washing Machine": 3.0
    }
    rows  = []
    dates = pd.date_range("2023-01-01", periods=8760, freq="h")
    for appliance in APPLIANCES:
        base = base_usage.get(appliance, 2.0)
        for ts in dates:
            val = max(0, base
                      + np.random.normal(0, base * 0.3)
                      + base * 0.3 * np.sin(2 * np.pi * ts.hour / 24))
            rows.append({
                "Appliance Type": appliance,
                "timestamp":      ts,
                "Energy Consumption (kWh)": round(val, 2)
            })
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════
# PREDICTION ENGINE
# ═══════════════════════════════════════════════════════════════════

def predict_next(appliance, historical_24h):
    """
    Predict the next hour's energy consumption.

    Args:
        appliance     : str — appliance name
        historical_24h: list of 24 float values (kWh, most recent last)

    Returns:
        float — predicted kWh for the next hour
    """
    sc = scalers.get(appliance)
    if sc is None:
        return round(float(np.mean(historical_24h)), 3)

    arr        = np.array(historical_24h, dtype=float).reshape(-1, 1)
    arr_scaled = sc.transform(arr)
    X          = arr_scaled.reshape(1, SEQ_LENGTH, 1)

    if appliance in models:
        # LSTM prediction
        pred_scaled = models[appliance].predict(X, verbose=0)
        pred        = sc.inverse_transform(pred_scaled.reshape(-1, 1))[0][0]
    else:
        # Statistical fallback: weighted moving average
        weights = np.linspace(0.5, 1.0, len(historical_24h))
        pred    = float(np.average(historical_24h, weights=weights))
        pred   += np.random.normal(0, pred * 0.05)

    return max(0.0, round(float(pred), 3))


# ═══════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Serve the web dashboard."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Health check — used by ngrok and monitoring."""
    return jsonify({"status": "ok", "models_loaded": len(models)})


@app.route("/api/overview")
def api_overview():
    """
    GET /api/overview
    Returns top-level KPI summary.
    """
    total_kwh = sum(s["total_kwh"] for s in app_stats_cache.values())
    avg_r2    = float(np.mean([s["r2"] for s in app_stats_cache.values()]))
    top_app   = max(app_stats_cache, key=lambda k: app_stats_cache[k]["total_kwh"])

    return jsonify({
        "total_kwh":      round(total_kwh, 2),
        "avg_r2":         round(avg_r2, 3),
        "num_appliances": len(APPLIANCES),
        "top_consumer":   top_app,
        "models_loaded":  len(models),
        "appliances":     list(app_stats_cache.keys())
    })


@app.route("/api/all_stats")
def api_all_stats():
    """
    GET /api/all_stats
    Returns summary stats for all appliances (no chart data).
    """
    summary = {}
    for appliance, stats in app_stats_cache.items():
        summary[appliance] = {
            "total_kwh": stats["total_kwh"],
            "avg_kwh":   stats["avg_kwh"],
            "max_kwh":   stats["max_kwh"],
            "r2":        stats["r2"],
            "mae":       stats["mae"],
            "rmse":      stats["rmse"],
            "has_model": stats["has_model"]
        }
    return jsonify(summary)


@app.route("/api/appliance/<path:name>")
def api_appliance(name):
    """
    GET /api/appliance/<name>
    Returns full stats + chart data for one appliance.
    Accepts spaces or underscores in name.
    """
    name = name.replace("_", " ")
    if name not in app_stats_cache:
        return jsonify({"error": f"Appliance '{name}' not found"}), 404
    return jsonify(app_stats_cache[name])


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    POST /api/predict
    Body: { "appliance": str, "historical_data": [float x 24] }
    Returns: { "appliance", "prediction", "unit", "model_type", "r2", "mae", "confidence" }
    """
    data = request.get_json(force=True)

    appliance = data.get("appliance", "")
    if not appliance or appliance not in APPLIANCES:
        return jsonify({"error": f"Invalid appliance: '{appliance}'"}), 400

    historical = data.get("historical_data", [])

    # Pad if shorter than SEQ_LENGTH
    if len(historical) < SEQ_LENGTH:
        mean_val   = float(np.mean(app_data.get(appliance, [2.0])))
        historical = [mean_val] * (SEQ_LENGTH - len(historical)) + list(historical)

    historical = [float(v) for v in historical[-SEQ_LENGTH:]]
    prediction = predict_next(appliance, historical)

    stats      = app_stats_cache.get(appliance, {})
    r2_val     = stats.get("r2", 0.0)
    confidence = "high" if r2_val > 0.7 else "medium" if r2_val > 0.4 else "low"

    return jsonify({
        "appliance":  appliance,
        "prediction": prediction,
        "unit":       "kWh",
        "model_type": "LSTM" if appliance in models else "Statistical Fallback",
        "r2":         r2_val,
        "mae":        stats.get("mae", 0.0),
        "confidence": confidence
    })


@app.route("/api/suggestions")
def api_suggestions():
    """
    GET /api/suggestions
    Returns smart energy-saving suggestions based on usage patterns.
    """
    suggestions = []
    icons = {
        "Air Conditioning": "❄️", "Heater":          "🔥",
        "Washing Machine":  "🫧", "Dishwasher":       "🍽️",
        "Fridge":           "🧊", "Oven":             "🍳",
        "Lights":           "💡", "Computer":         "💻",
        "TV":               "📺", "Microwave":        "📡"
    }
    tips = {
        "Air Conditioning": "Set thermostat to 24-26°C — reduces consumption by up to 20%.",
        "Heater":           "Lower heating by 1°C to save ~7% on heating bills.",
        "Washing Machine":  "Wash at 30°C instead of 60°C — saves 40% energy per cycle.",
        "Dishwasher":       "Use eco mode — uses 20-40% less energy than standard mode.",
        "Fridge":           "Set to 3-5°C optimal temperature and defrost regularly.",
        "Oven":             "Use microwave for small portions — 80% less energy than oven.",
        "Lights":           "Switch to LED bulbs — 75% less energy than incandescent.",
        "Computer":         "Enable sleep mode after 10 minutes idle — saves background power.",
        "TV":               "Enable auto-brightness to save up to 15% screen energy.",
        "Microwave":        "Cover food while cooking to retain heat and reduce cook time."
    }
    colors = ["#ff4d6d", "#ff6b35", "#ffb830", "#00e5a0", "#9d6fff"]

    # Top 5 consumers
    ranked = sorted(
        app_stats_cache.items(),
        key=lambda x: x[1]["total_kwh"],
        reverse=True
    )
    for i, (appliance, stats) in enumerate(ranked[:5]):
        suggestions.append({
            "appliance":       appliance,
            "icon":            icons.get(appliance, "⚡"),
            "title":           f"{appliance} — Top Consumer #{i + 1}",
            "detail":          f"{stats['total_kwh']:.0f} kWh total | avg {stats['avg_kwh']:.2f} kWh/hr",
            "tip":             tips.get(appliance, "Monitor and reduce peak-hour usage."),
            "saving_potential":"HIGH" if i < 2 else "MEDIUM",
            "color":           colors[i % len(colors)]
        })

    # Off-peak scheduling tip
    suggestions.append({
        "appliance": "All Appliances",
        "icon":      "☀️",
        "title":     "Shift Loads to Off-Peak Hours",
        "detail":    "Off-peak electricity (10pm–6am) costs 30-40% less in most regions.",
        "tip":       "Schedule washing machine, dishwasher, and EV charging for night-time.",
        "saving_potential": "HIGH",
        "color": "#00d4ff"
    })

    # Budget tip
    total = sum(s["total_kwh"] for s in app_stats_cache.values())
    suggestions.append({
        "appliance": "All Appliances",
        "icon":      "📊",
        "title":     "Set a Monthly Energy Budget",
        "detail":    f"Current total usage: {total:.0f} kWh. Target a 10% monthly reduction.",
        "tip":       "Use LSTM predictions to anticipate high-usage days and adjust habits.",
        "saving_potential": "MEDIUM",
        "color": "#6366f1"
    })

    return jsonify(suggestions)


# ═══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("⚡ Smart Energy Monitor — Starting up")
    print("=" * 60)
    load_everything()
    print("\n[SERVER] Running at http://localhost:5000")
    print("[SERVER] Press Ctrl+C to stop\n")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False
    )
