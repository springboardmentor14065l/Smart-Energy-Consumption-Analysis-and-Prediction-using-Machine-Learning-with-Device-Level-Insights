# Energy Consumption Forecasting (LSTM + Dashboard)

## 1) Overview

This project analyzes household energy consumption data and builds machine learning models to **forecast the next time-step energy consumption (kWh)**. The final deliverable is a **Flask web dashboard** that:

- Visualizes energy usage at multiple time granularities (hourly, daily, weekly, monthly)
- Shows appliance-wise consumption charts
- Provides basic energy-saving suggestions
- Predicts the next consumption value using pre-trained LSTM models

## 2) Work completed

### A) Data cleaning and exploration

- Used the raw dataset in [dataset/original/consumption.xlsx](dataset/original/consumption.xlsx)
- Cleaned the data and standardized key columns (dates/times and numeric fields)
- Produced a single cleaned dataset used by both notebooks and the dashboard:
  - [dataset/Cleaned/cleaned_sorted_energy_dataset.xlsx](dataset/Cleaned/cleaned_sorted_energy_dataset.xlsx)

Notebook used:

- [Cleaning and exploration/Cleaning.ipynb](Cleaning%20and%20exploration/Cleaning.ipynb)

### B) Feature engineering

- Created model-ready features from time and context information (for example: hour, day, weekday, month)
- Prepared appliance-wise and home-wise sequences required for time-series forecasting

Notebook used:

- [Feature engineering/Feature.ipynb](Feature%20engineering/Feature.ipynb)

### C) Baseline regression model

- Implemented a baseline regression approach to compare against deep learning performance
- Used the baseline results as a reference before moving to LSTM

Notebook used:

- [Baseline regression model/Baseline_regression_model.ipynb](Baseline%20regression%20model/Baseline_regression_model.ipynb)

### D) LSTM model training (per appliance)

- Trained LSTM models to predict next-step energy consumption
- Trained separate models for each appliance type and saved them as `.h5` files
- Created train/test splits and saved them as CSV files per appliance

Notebook used:

- [LSTM MODEL/Lstm.ipynb](LSTM%20MODEL/Lstm.ipynb)

Saved model artifacts:

- General saved artifact from experimentation: [LSTM MODEL/lstm_energy_model.h5](LSTM%20MODEL/lstm_energy_model.h5)
- Per-appliance models used by the dashboard: [models/](models/)

### E) Model evaluation (MAE/RMSE)

Model evaluation metrics (per appliance) are stored in:

- [outputs/lstm_metrics_per_appliance.csv](outputs/lstm_metrics_per_appliance.csv)

The file includes columns such as: `appliance`, `homes_used`, `mae`, `rmse`, `train_samples`, `test_samples`, and `model_path`.

### F) Dashboard implementation

A local web dashboard was developed that:

- Loads the cleaned dataset Excel file
- Aggregates overall usage and device-wise usage
- Generates charts with matplotlib
- Serves predictions using the LSTM `.h5` models

Main backend and UI files:

- Backend API: [dashboard/app.py](dashboard/app.py)
- UI page: [dashboard/templates/index.html](dashboard/templates/index.html)
- Frontend logic: [dashboard/static/app.js](dashboard/static/app.js)
- Styling: [dashboard/static/styles.css](dashboard/static/styles.css)

## 3) How to run the dashboard (Windows)

Run the dashboard using the PowerShell script:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_dashboard.ps1
```

- URL: http://127.0.0.1:5000
- To run without opening the browser automatically:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_dashboard.ps1 -NoBrowser
```

What this script does:

- Creates a local virtual environment in `.venv/` (if it does not exist)
- Installs dependencies from [requirements.txt](requirements.txt)
- Starts the Flask application

## 4) Data and model notes

### Cleaned dataset used by the dashboard

The dashboard reads:

- [dataset/Cleaned/cleaned_sorted_energy_dataset.xlsx](dataset/Cleaned/cleaned_sorted_energy_dataset.xlsx)

The backend expects columns including:

- `Date`, `Hour`, `Home ID`, `Appliance Type`
- `Energy Consumption (kWh)`
- `Outdoor Temperature (C)`, `Household Size`

### Train/test split files

The folder [dataset/processed_appliance_data/](dataset/processed_appliance_data/) contains per-appliance train/test CSVs named like:

- `X_train_<Appliance>.csv`, `X_test_<Appliance>.csv`
- `y_train_<Appliance>.csv`, `y_test_<Appliance>.csv`

Example files:

- [dataset/processed_appliance_data/X_train_Fridge.csv](dataset/processed_appliance_data/X_train_Fridge.csv)
- [dataset/processed_appliance_data/y_test_TV.csv](dataset/processed_appliance_data/y_test_TV.csv)

### Dashboard prediction model naming

The dashboard loads models from [models/](models/) using a naming rule:

- `lstm_<ApplianceNameWithUnderscores>_top50_ts8.h5`

Examples:

- [models/lstm_Fridge_top50_ts8.h5](models/lstm_Fridge_top50_ts8.h5)
- [models/lstm_Washing_Machine_top50_ts8.h5](models/lstm_Washing_Machine_top50_ts8.h5)

## 5) File map (concise)

- Root
  - [requirements.txt](requirements.txt)
  - [run_dashboard.ps1](run_dashboard.ps1)
  - [.gitignore](.gitignore)
  - `.venv/` (generated locally)
- Notebooks
  - [Cleaning and exploration/Cleaning.ipynb](Cleaning%20and%20exploration/Cleaning.ipynb)
  - [Feature engineering/Feature.ipynb](Feature%20engineering/Feature.ipynb)
  - [Baseline regression model/Baseline_regression_model.ipynb](Baseline%20regression%20model/Baseline_regression_model.ipynb)
  - [LSTM MODEL/Lstm.ipynb](LSTM%20MODEL/Lstm.ipynb)
- Dashboard
  - [dashboard/app.py](dashboard/app.py)
  - [dashboard/templates/index.html](dashboard/templates/index.html)
  - [dashboard/static/app.js](dashboard/static/app.js)
  - [dashboard/static/styles.css](dashboard/static/styles.css)
- Data
  - [dataset/original/consumption.xlsx](dataset/original/consumption.xlsx)
  - [dataset/Cleaned/cleaned_sorted_energy_dataset.xlsx](dataset/Cleaned/cleaned_sorted_energy_dataset.xlsx)
  - [dataset/processed_appliance_data/](dataset/processed_appliance_data/)
- Models
  - [models/](models/)
  - [LSTM MODEL/lstm_energy_model.h5](LSTM%20MODEL/lstm_energy_model.h5)
- Outputs
  - [outputs/lstm_metrics_per_appliance.csv](outputs/lstm_metrics_per_appliance.csv)
  - [outputs/probe_charts.py](outputs/probe_charts.py)
