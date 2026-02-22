import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Smart Energy Dashboard",
    layout="wide",
    page_icon="⚡"
)

# ---------------- TITLE ----------------
st.title("⚡ Smart Energy Consumption Dashboard")
st.caption("Real-time monitoring, analysis and smart insights")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("smart_home_energy_consumption_large.csv")
    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔎 Filters")

device = st.sidebar.selectbox(
    "Select Appliance",
    df["Appliance Type"].unique()
)

time_view = st.sidebar.selectbox(
    "Select Time View",
    ["Raw Data", "Daily", "Monthly"]
)

filtered = df[df["Appliance Type"] == device]

# ---------------- TIME AGGREGATION ----------------
if time_view != "Raw Data":
    filtered["Date"] = pd.to_datetime(filtered["Date"])
    filtered.set_index("Date", inplace=True)

    if time_view == "Daily":
        filtered = filtered.resample("D").sum()

    if time_view == "Monthly":
        filtered = filtered.resample("M").sum()

# ---------------- KPI CARDS ----------------
st.subheader("📊 Key Performance Indicators")

c1, c2, c3 = st.columns(3)

total = filtered["Energy Consumption (kWh)"].sum()
avg = filtered["Energy Consumption (kWh)"].mean()
peak = filtered["Energy Consumption (kWh)"].max()

c1.metric("Total Energy", f"{total:.2f} kWh")
c2.metric("Average Usage", f"{avg:.2f} kWh")
c3.metric("Peak Usage", f"{peak:.2f} kWh")

st.divider()

# ---------------- LINE TREND ----------------
st.subheader("📈 Energy Consumption Trend")

fig = px.line(
    filtered.reset_index(),
    y="Energy Consumption (kWh)",
    title=f"{device} Usage Trend"
)
st.plotly_chart(fig, use_container_width=True)

# ---------------- DISTRIBUTION ----------------
st.subheader("📊 Consumption Distribution")

fig2 = px.histogram(
    filtered.reset_index(),
    x="Energy Consumption (kWh)",
    nbins=40,
    title="Energy Distribution"
)
st.plotly_chart(fig2, use_container_width=True)

# ---------------- DEVICE SHARE ----------------
st.subheader("🥧 Energy Share by Device")

device_total = df.groupby("Appliance Type")["Energy Consumption (kWh)"].sum()

fig3 = px.pie(
    values=device_total.values,
    names=device_total.index,
    title="Total Energy Share"
)
st.plotly_chart(fig3, use_container_width=True)

# ---------------- SMART INSIGHTS ----------------
st.subheader("💡 Smart Energy Insights")

highest_device = device_total.idxmax()
highest_value = device_total.max()

st.warning(f"{highest_device} consumes highest energy ({highest_value:.2f} kWh).")

if peak > avg * 1.5:
    st.error("High peak usage detected. Avoid running heavy appliances together.")

st.success("Tip: Use appliances during non-peak hours to reduce electricity bills.")
# ---------------- ML PREDICTION ----------------
st.subheader("🔮 Energy Consumption Prediction")

from sklearn.linear_model import LinearRegression
import numpy as np

# Prepare data for prediction
data = filtered.reset_index().copy()
data["index"] = np.arange(len(data))

X = data[["index"]]
y = data["Energy Consumption (kWh)"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Predict future 20 steps
future_steps = 20
future_index = np.arange(len(data), len(data) + future_steps).reshape(-1, 1)
future_pred = model.predict(future_index)

# Plot prediction
import plotly.graph_objects as go

fig_pred = go.Figure()

fig_pred.add_trace(go.Scatter(
    y=y,
    mode="lines",
    name="Actual"
))

fig_pred.add_trace(go.Scatter(
    x=np.arange(len(data), len(data)+future_steps),
    y=future_pred,
    mode="lines",
    name="Predicted"
))

fig_pred.update_layout(title="Future Energy Prediction")

st.plotly_chart(fig_pred, use_container_width=True)
