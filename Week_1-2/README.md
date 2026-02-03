Smart Energy Consumption Analysis and Prediction Using Machine Learning with Device-Level Insights

# Energy Consumption Analysis & Feature Engineering

Project Overview

This project analyzes household device energy consumption using timestamped data. It includes **basic data preprocessing**, **feature engineering**and **visualization** to understand energy usage patterns across devices and time.

Dataset Description

The dataset contains the following columns:

* timestamp: Date and time when energy was recorded
* device: Name of the electrical device
* energy: Energy consumption in kWh

Sample devices include AC, Fridge, TV, Fan, Washing Machine, and Light.
 Data Preprocessing

* Converted `timestamp` to datetime format
* Extracted **hour** from timestamp
* Encoded device names using **categorical codes** for modeling
Feature Engineering

The following new features were created:

* hour: Hour of the day (0–23)
* day_period: Time of day (Morning, Afternoon, Evening, Night)
* device_code: Numeric encoding of device names
* is_high_power_device: Binary flag for high-power devices (AC, Washing Machine)
* device_usage_count: Frequency of device usage
* avg_device_energy: Average energy consumption per device
* is_peak_hour: Indicates peak usage hours (8 AM – 11 AM)

Machine Learning Model

* Model Used: Linear Regression
* Input Features: `hour`, `device_code`
* Target Variable: `energy`
* Dataset split into training (70%) and testing (30%)

Visualization
A bar chart is used to display:
    Total Energy Consumption per Device
   This helps identify devices with higher overall energy usage.