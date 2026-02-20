from flask import Flask, render_template, jsonify, request
import pandas as pd

app = Flask(__name__)

daily = pd.read_csv("daily_device_energy.csv")
device = pd.read_csv("device_level.csv")


@app.route("/")
def home():
    return render_template("index.html")


# ================= KPI =================
@app.route("/kpi")
def kpi():

    mode=request.args.get("mode","daily")
    df=daily.copy()

    date_col=None
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            date_col=col
            break

    if date_col is None:
        date_col=df.columns[0]

    df[date_col]=pd.to_datetime(df[date_col],errors="coerce")
    df=df.dropna(subset=[date_col])

    df["total"]=df.select_dtypes(include=['number']).sum(axis=1)

    # ---- grouping logic ----
    if mode=="weekly":
        grouped=df.groupby(df[date_col].dt.to_period("W"))["total"].sum()

    elif mode=="monthly":
        grouped=df.groupby(df[date_col].dt.to_period("M"))["total"].sum()

    else:
        grouped=df.groupby(df[date_col].dt.date)["total"].sum()

    total=grouped.sum()

    # normalize
    total=total/1000
    if total>10000:
        total=total/365

    intensity=total/len(grouped)
    carbon=total*0.82
    cost=total*6

    return jsonify({
        "intensity":round(intensity,2),
        "carbon":round(carbon,2),
        "cost":round(cost,2)
    })


# ================= CHART DATA =================
@app.route("/daily")
def daily_chart():

    mode=request.args.get("mode","daily")
    df=daily.copy()

    date_col=None
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            date_col=col
            break

    if date_col is None:
        date_col=df.columns[0]

    df[date_col]=pd.to_datetime(df[date_col],errors="coerce")
    df=df.dropna(subset=[date_col])

    df["total"]=df.select_dtypes(include=['number']).sum(axis=1)

    if mode=="weekly":
        grouped=df.groupby(df[date_col].dt.to_period("W"))["total"].sum()

    elif mode=="monthly":
        grouped=df.groupby(df[date_col].dt.to_period("M"))["total"].sum()

    else:
        grouped=df.groupby(df[date_col].dt.date)["total"].sum()

    grouped=grouped.sort_index()

    values=[float(v/1000) for v in grouped.values]

    return jsonify({
        "labels":[str(i) for i in grouped.index],
        "values":values
    })


# ================= DEVICES =================
@app.route("/devices")
def devices():

    df=device.copy()

    device_col=df.select_dtypes(include=['object']).columns[0]
    energy_col=df.select_dtypes(include=['number']).columns[0]

    totals=df.groupby(device_col)[energy_col].sum()
    totals=totals/1000

    return jsonify({k:float(v) for k,v in totals.items()})


# ================= DEVICE COST =================
@app.route("/device-cost")
def device_cost():

    df=device.copy()

    device_col=df.select_dtypes(include=['object']).columns[0]
    energy_col=df.select_dtypes(include=['number']).columns[0]

    totals=df.groupby(device_col)[energy_col].sum()

    result={}

    for name,units in totals.items():

        units=units/1000
        if units>10000:
            units=units/365

        if units<5:
            rate=3
        elif units<15:
            rate=5
        elif units<30:
            rate=6.5
        else:
            rate=8

        result[name]={
            "units":round(units,2),
            "cost":round(units*rate,2)
        }

    return jsonify(result)


if __name__=="__main__":
    app.run(debug=True)
