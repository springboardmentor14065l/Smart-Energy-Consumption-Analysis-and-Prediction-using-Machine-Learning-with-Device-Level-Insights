# AI-Driven Energy Consumption Forecasting

## Project Overview

This project focuses on building an end-to-end machine learning pipeline for **smart home energy consumption analysis and forecasting**. The objective is to understand historical device-level energy usage, perform systematic preprocessing and feature engineering, establish a strong baseline model, and then improve forecasting performance using advanced deep learning (LSTM) techniques.

The project has been executed in a **week-wise, milestone-driven manner**, following industry-standard ML workflow and GitHub collaboration practices.

---

## Tools & Technologies

* **Programming Language:** Python
* **Development Environment:** Google Colab
* **Libraries:** Pandas, NumPy, Matplotlib, Scikit-learn, TensorFlow/Keras
* **Version Control:** Git & GitHub (branch-based workflow)
* **Data Format:** CSV

---

## Dataset Description

* Smart Home Energy Monitoring Dataset
* Granularity: Device-level energy consumption
* Time-based data containing Date and Time columns
* Target variable: Energy Consumption (kWh)

---

## Week 1–2: Data Collection, Understanding & Preprocessing

### Objectives

* Understand the dataset structure and variables
* Clean raw data and fix inconsistencies
* Prepare a reliable dataset for ML modeling

### Work Done

* Loaded and explored the dataset using Pandas
* Checked data types, null values, and basic statistics
* Created unified **timestamp** column by combining Date and Time
* Sorted data chronologically
* Verified data integrity
* Removed abnormal values (outliers) using quantile-based filtering
* Resampled energy data into **hourly** and **daily** formats
* Visualized appliance-wise energy consumption trends
* Saved cleaned and processed datasets for further stages

### Outcome

A clean, structured, and time-aligned dataset ready for feature engineering and modeling.

---

## Week 3–4: Feature Engineering & Baseline Model Development

### Objectives

* Extract meaningful features from time-series data
* Establish a baseline forecasting model for comparison

### Feature Engineering (Week 3)

* Extracted time-based features:

  * Hour of day
  * Day of month
  * Weekday
* Created lag features:

  * Previous hour (lag_1)
  * Same hour previous day (lag_24)
* Generated rolling statistics:

  * 24-hour rolling mean
* Prepared final feature set for ML input

### Baseline Model Development (Week 4)

* Implemented **Linear Regression** as baseline model
* Split data into:

  * 70% Training
  * 30% Testing (time-aware split)
* Trained baseline model on engineered features
* Evaluated using:

  * MAE (Mean Absolute Error)
  * RMSE (Root Mean Squared Error)
* Visualized actual vs predicted energy consumption

### Outcome

A simple but interpretable baseline model that provides a reference point for advanced models.

---

## Week 5–6: LSTM Model Development, Evaluation & Integration

### Objectives

* Capture temporal dependencies using deep learning
* Improve forecasting accuracy beyond baseline
* Prepare model for deployment readiness

### LSTM Model Development (Week 5)

* Implemented **Long Short-Term Memory (LSTM)** networks using TensorFlow/Keras
* Converted time-series data into sequential format using sliding windows
* Trained **appliance-wise LSTM models** to capture device-specific patterns
* Tuned hyperparameters (epochs, batch size, learning rate)
* Applied **EarlyStopping** to prevent overfitting

### Model Evaluation & Integration (Week 6)

* Evaluated LSTM models using:

  * MAE
  * RMSE
  * R² Score
* Compared LSTM performance against baseline Linear Regression
* Observed:

  * Lower errors for stable appliances (e.g., Fridge)
  * Higher errors for variable appliances (e.g., AC, Heater)
* Saved trained models, scalers, and training histories
* Implemented and tested prediction functions suitable for Flask/API integration

### Outcome

A fully trained, evaluated, and deployment-ready LSTM forecasting pipeline with improved temporal learning.

---

## GitHub Workflow & Project Organization

### Branch Strategy

* All work performed on **individual feature branches**
* No direct commits to main branch

### Repository Structure

```
Project-Repository/
├── Week-1-2/
├── Week-3-4/
├── Week-5-6/
│   ├── LSTM_Model.ipynb
│   ├── lstm_models/
│   └── README.md
├── documents/
│   ├── Week-1-2.md
│   ├── Week-3-4.md
│   └── Week-5-6.md
└── README.md
```

### Documentation

* Each week documented separately
* Clear explanation of objectives, methods, and outcomes

---

## Current Project Status

✅ Data preprocessing completed
✅ Feature engineering completed
✅ Baseline Linear Regression implemented
✅ LSTM models trained and evaluated
✅ Models saved and validated
✅ Documentation maintained

The project is currently **on track and up to date through Week 6**.

---

## Conclusion

This project demonstrates a complete machine learning workflow—from raw data processing to advanced deep learning-based forecasting—implemented with structured experimentation, proper version control, and professional documentation practices.
