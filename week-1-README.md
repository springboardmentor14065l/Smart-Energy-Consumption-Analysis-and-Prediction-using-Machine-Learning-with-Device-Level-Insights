# Week 1: Data Understanding & Preprocessing

## Objective
The goal of Week 1 was to understand the raw smart home energy consumption dataset,
perform data cleaning, and analyze timestamp-based energy consumption trends.

---

## Dataset
- Source: Smart Home Energy Consumption Dataset
- File used: smart_home_energy_consumption_large.csv
- Data type: Raw, unprocessed data

---

## Tasks Performed

### 1. Data Understanding
- Loaded the raw dataset
- Inspected structure using `head()`, `info()`, and `describe()`
- Identified data types and column meanings
- Checked for missing and null values

Notebook:
- `notebooks/week1/data_cleaning.ipynb`

---

### 2. Data Cleaning
- Verified missing values in each column
- Ensured correct data types for numerical and categorical columns
- Confirmed dataset consistency

Notebook:
- `notebooks/week1/data_cleaning.ipynb`

---

### 3. Timestamp Analysis
- Combined Date and Time columns into a single datetime format
- Converted datetime column into index
- Performed resampling to analyze daily energy consumption
- Visualized energy consumption trends over time

Notebooks:
- `notebooks/week1/timestamp_analysis.ipynb`
- `notebooks/week1/daily_energy_consumption_trend.ipynb`

---

## Key Observations
- Energy consumption varies significantly across different dates
- Daily average consumption shows fluctuations over time
- Timestamp-based analysis helps identify usage patterns

---

## Output of Week 1
- Cleaned and structured dataset ready for feature engineering
- Time-based insights into energy consumption behavior
