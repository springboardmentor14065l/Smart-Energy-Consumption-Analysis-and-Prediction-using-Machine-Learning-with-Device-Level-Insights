from flask import Flask, render_template, jsonify, request
import pandas as pd

app = Flask(__name__)

# ================= LOAD DATA =================
hourly = pd.read_csv("hourly_device_energy.csv")
device = pd.read_csv("device_level.csv")

# Convert timestamp column to datetime
hourly['timestamp'] = pd.to_datetime(hourly['timestamp'], errors='coerce')

# Remove invalid timestamps
hourly = hourly.dropna(subset=['timestamp'])

# Set index for proper resampling (Better for time-series models)
hourly.set_index('timestamp', inplace=True)

# Create daily aggregated data
daily = hourly.resample('D').sum(numeric_only=True).reset_index()


# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html")


# ================= KPI =================
@app.route("/kpi")
def kpi():

    mode = request.args.get("mode", "daily")
    df = daily.copy()

    df["total"] = df.select_dtypes(include=['number']).sum(axis=1)

    # ---- grouping logic ----
    if mode == "weekly":
        grouped = df.groupby(df['timestamp'].dt.to_period("W"))["total"].sum()

    elif mode == "monthly":
        grouped = df.groupby(df['timestamp'].dt.to_period("M"))["total"].sum()

    else:
        grouped = df.groupby(df['timestamp'].dt.date)["total"].sum()

    total = grouped.sum()

    # Normalize to kWh
    total = total / 1000

    if total > 10000:
        total = total / 365

    intensity = total / len(grouped)
    carbon = total * 0.82
    cost = total * 6

    return jsonify({
        "intensity": round(intensity, 2),
        "carbon": round(carbon, 2),
        "cost": round(cost, 2)
    })


# ================= CHART DATA =================
@app.route("/daily")
def daily_chart():

    mode = request.args.get("mode", "daily")
    df = daily.copy()

    df["total"] = df.select_dtypes(include=['number']).sum(axis=1)

    if mode == "weekly":
        grouped = df.groupby(df['timestamp'].dt.to_period("W"))["total"].sum()

    elif mode == "monthly":
        grouped = df.groupby(df['timestamp'].dt.to_period("M"))["total"].sum()

    else:
        grouped = df.groupby(df['timestamp'].dt.date)["total"].sum()

    grouped = grouped.sort_index()

    values = [float(v / 1000) for v in grouped.values]

    return jsonify({
        "labels": [str(i) for i in grouped.index],
        "values": values
    })


# ================= DEVICES (ADVANCED ANALYTICS) =================
@app.route("/devices")
def devices():

    df = device.copy()

    device_col = df.select_dtypes(include=['object']).columns[0]
    energy_col = df.select_dtypes(include=['number']).columns[0]

    # Total consumption per device
    totals = df.groupby(device_col)[energy_col].sum() / 1000  # kWh

    # Percentage contribution
    percentage = (totals / totals.sum()) * 100

    # Variability (Standard Deviation)
    variability = df.groupby(device_col)[energy_col].std() / 1000

    insight_df = pd.DataFrame({
        "total_kwh": totals,
        "percentage": percentage,
        "std_dev": variability
    }).sort_values(by="percentage", ascending=False)

    result = {}

    for device_name, row in insight_df.iterrows():
        result[device_name] = {
            "total_kwh": round(row["total_kwh"], 2),
            "percentage": round(row["percentage"], 2),
            "std_dev": round(row["std_dev"], 2)
        }

    return jsonify(result)


# ================= DEVICE COST =================
@app.route("/device-cost")
def device_cost():

    df = device.copy()

    device_col = df.select_dtypes(include=['object']).columns[0]
    energy_col = df.select_dtypes(include=['number']).columns[0]

    totals = df.groupby(device_col)[energy_col].sum()

    result = {}

    for name, units in totals.items():

        units = units / 1000  # convert to kWh

        if units > 10000:
            units = units / 365

        # Dynamic slab rate
        if units < 5:
            rate = 3
        elif units < 15:
            rate = 5
        elif units < 30:
            rate = 6.5
        else:
            rate = 8

        result[name] = {
            "units": round(units, 2),
            "cost": round(units * rate, 2)
        }

    return jsonify(result)


# ================= RUN APP =================
if __name__ == "__main__":
    app.run(debug=True
            )