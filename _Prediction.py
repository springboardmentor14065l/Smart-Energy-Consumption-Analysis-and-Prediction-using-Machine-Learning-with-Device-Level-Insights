import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

st.title("🔮 Energy Consumption Prediction")

# Load data
df = pd.read_csv("smart_home_energy_consumption_large.csv")

# Device select
device = st.selectbox("Select Appliance", df["Appliance Type"].unique())

data = df[df["Appliance Type"] == device].copy()

# Create time index
data = data.reset_index()
data["time_index"] = np.arange(len(data))

X = data[["time_index"]]
y = data["Energy Consumption (kWh)"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Predict future
future_days = st.slider("Select future prediction steps", 10, 100, 30)

future_index = np.arange(len(data), len(data)+future_days).reshape(-1,1)
future_pred = model.predict(future_index)

# Plot graph
fig = go.Figure()

fig.add_trace(go.Scatter(
    y=y,
    mode="lines",
    name="Actual Usage"
))

fig.add_trace(go.Scatter(
    x=np.arange(len(data), len(data)+future_days),
    y=future_pred,
    mode="lines",
    name="Predicted Usage"
))

fig.update_layout(
    title="Energy Forecast",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

st.success("Prediction generated using Linear Regression model.")