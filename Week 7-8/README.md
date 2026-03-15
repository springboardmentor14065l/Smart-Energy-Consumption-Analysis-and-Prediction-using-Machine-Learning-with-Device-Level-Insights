# Week 7-8: Dashboard and Visualization

This module provides an interactive web dashboard for monitoring energy consumption and predicting future demand using a trained LSTM model.

## Features
- **Real-time Stats**: Displays total consumption, average hourly usage, and peak usage.
- **LSTM Prediction**: Predicts energy consumption for the next hour based on the last 24 hours of data.
- **Dynamic Charts**:
    - Hourly energy consumption trends.
    - Daily consumption for the last 7 days.
    - Device-wise energy distribution (Pie chart).
- **Goal-Driven Smart Energy Advisor**: Personalized suggestions based on four distinct goals: Reduce Bills, Reduce Carbon Footprint, Avoid Peak Charges, and General Monitoring.
- **LSTM Prediction**: Real-time energy consumption forecasting for the next hour.
- **Premium Glassmorphism UI**: High-impact, interactive dashboard with crystal-clear visual aesthetics and micro-animations.
- **Dynamic Insight Engine**: Behavioral alerts and context-aware energy-saving tips based on device-level usage.

## Project Structure
- `app.py`: Main Flask application.
- `prediction_engine.py`: ML integration layer (Model loading & prediction).
- `visualization.py`: Matplotlib chart generation.
- `templates/`: HTML templates.
- `static/`: CSS, JS, and generated chart images.

## Setup and Usage

### 1. Create Virtual Environment
Create a virtual environment named `infosys_internship` in the project root:
```bash
python -m venv infosys_internship
```

### 2. Activate and Install Dependencies
Activate the environment and install the required libraries:
```powershell
# Windows
.\infosys_internship\Scripts\Activate.ps1
pip install -r "Week 7-8\requirements.txt"
```

### 3. Run the Application
From the project root, run the application using the virtual environment's Python:
```bash
.\infosys_internship\Scripts\python "Week 7-8\app.py"
```

### 3. Access the Dashboard
Open your browser and go to:
[http://localhost:5000](http://localhost:5000)

## How it Works
1. When the dashboard loads (or when Refreshed), the `visualization.py` script generates new charts from the latest dataset.
2. The `prediction_engine.py` loads the saved LSTM model (`lstm_energy_model.h5`) and the MinMaxScaler.
3. The Flask API provides endpoints for the frontend to fetch statistics, predictions, and suggestions dynamically.
