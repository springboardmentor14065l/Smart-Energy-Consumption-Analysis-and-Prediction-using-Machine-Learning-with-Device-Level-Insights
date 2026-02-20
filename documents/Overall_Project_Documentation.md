# AI-Driven Smart Energy Consumption Forecasting with Device-Level Insights

## Project Overview

This project presents a complete end-to-end machine learning system for analyzing and forecasting smart home energy consumption at the device level.  
The objective is to transform raw energy usage data into actionable insights and accurate forecasts using a structured ML pipeline—starting from data preprocessing and feature engineering, progressing through baseline modeling and deep learning, and finally deploying the model via a web-based dashboard.

The project was executed in a week-wise, milestone-driven format, following industry-standard ML workflows, documentation practices, and GitHub collaboration guidelines.

---

## Tools & Technologies

### Programming Language
- Python

### Development Environment
- Google Colab

### Libraries & Frameworks
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- TensorFlow / Keras
- Flask

### Version Control
- Git & GitHub (branch-based workflow)

### Deployment & Demo
- Flask + Colab Tunneling

### Data Format
- CSV

---

## Dataset Description

- **Dataset:** Smart Home Energy Monitoring Dataset  
- **Granularity:** Device-level energy consumption  
- **Time Resolution:** Timestamped readings  
- **Target Variable:** Energy Consumption (kWh)

### Devices Included
- Air Conditioning  
- Computer  
- Dishwasher  
- Fridge  
- Heater  
- Lights  
- Microwave  
- Oven  
- TV  
- Washing Machine  

---

## Week 1–2: Data Collection, Understanding & Preprocessing

### Objectives
- Understand dataset structure and semantics  
- Clean and standardize raw data  
- Prepare a reliable dataset for modeling  

### Work Performed
- Loaded dataset and performed exploratory analysis  
- Verified schema, data types, and missing values  
- Combined date and time columns into a unified timestamp  
- Sorted records chronologically to preserve temporal order  
- Identified and removed outliers using quantile-based filtering  
- Resampled raw readings into hourly and daily energy usage  
- Visualized appliance-wise energy consumption patterns  
- Validated data consistency after preprocessing  
- Exported cleaned datasets for downstream tasks  

### Outcome
A clean, time-aligned, and structured dataset ready for feature engineering and modeling.

---

## Week 3–4: Feature Engineering & Baseline Model Development

### Objectives
- Extract informative temporal features  
- Establish a baseline forecasting model  

### Week 3: Feature Engineering
- Extracted time-based features:
  - Hour of day  
  - Day of month  
  - Weekday  

- Created lag features:
  - Previous hour consumption (lag_1)  
  - Same hour previous day (lag_24)  

- Generated rolling statistics:
  - 24-hour rolling mean  

- Prepared final ML-ready feature matrix  
- Performed appliance-wise feature preparation  

### Week 4: Baseline Model Development
- Implemented Linear Regression as a baseline forecasting model  
- Applied time-aware splitting:
  - 70% training  
  - 30% testing  

- Trained model on engineered features  
- Evaluated using:
  - Mean Absolute Error (MAE)  
  - Root Mean Squared Error (RMSE)  

- Visualized actual vs predicted energy consumption  
- Established baseline performance for comparison  

### Outcome
A simple, interpretable baseline model that serves as a benchmark for advanced models.

---

## Week 5–6: LSTM Model Development, Evaluation & Integration

### Objectives
- Capture long-term temporal dependencies  
- Improve forecasting accuracy  
- Prepare models for deployment  

### Week 5: LSTM Model Development
- Designed and implemented Long Short-Term Memory (LSTM) networks using TensorFlow/Keras  
- Transformed time-series data into sequential sliding windows  
- Built separate LSTM models for each appliance  
- Applied feature scaling using Min-Max normalization  
- Tuned hyperparameters:
  - Epochs  
  - Batch size  
  - Learning rate  

- Used EarlyStopping to prevent overfitting and improve generalization  

### Week 6: Model Evaluation & Integration
- Evaluated LSTM models using:
  - MAE  
  - RMSE  
  - R² Score  

- Compared LSTM results with baseline Linear Regression  
- Observed:
  - Lower errors for stable appliances (e.g., Fridge, Lights)  
  - Higher errors for variable appliances (e.g., AC, Heater)  

- Saved:
  - Trained LSTM models  
  - Scalers  
  - Training histories  

- Implemented reusable prediction functions compatible with Flask/API integration  

### Outcome
A robust, appliance-wise deep learning forecasting system with significantly improved temporal learning.

---

## Week 7–8: Model Integration, Dashboard & Finalization

### Objectives
- Deploy trained models via backend API  
- Create an interactive user interface  
- Prepare project for final demo and evaluation  

### Backend Integration (Flask)
- Integrated trained LSTM models into a Flask backend  
- Loaded appliance-specific models and scalers dynamically  
- Implemented REST-style prediction endpoints  
- Ensured modular and reusable backend architecture  

### Dashboard Development
- Developed a web-based interactive dashboard using:
  - HTML  
  - CSS  
  - Flask templates  

- Enabled users to:
  - Select appliances  
  - Input sample energy values  
  - View predicted energy consumption  

- Displayed device-wise predictions and insights  

### Finalization & Documentation
- Organized repository using clear week-wise folder structure  
- Added detailed README files for each phase  
- Created a centralized documents/ folder containing:
  - Week-wise documentation  
  - Milestone-wise summaries  

- Prepared project for demo, rehearsal, and final evaluation  

### Outcome
A complete, deployable, and demo-ready ML system with backend, UI, and documentation.

---

## GitHub Workflow & Project Organization

### Branch Strategy
- All work completed on individual branches  
- No direct commits to main  
- Clean commit history with week-wise messages  


### Repository Structure
```text
Project-Repository/
├── Week-1-2/
├── Week-3-4/
├── Week-5-6/
│   ├── LSTM_Model.ipynb
│   ├── lstm_models/
│   └── README.md
├── Week-7-8/
│   ├── flask_app/
│   ├── dashboard_notebook.ipynb
│   └── README.md
├── documents/
│   ├── Week-1-2.md
│   ├── Week-3-4.md
│   ├── Week-5-6.md
│   └── Week-7-8.md
└── README.md
-└── README.md
```
---

## Project Status

- ✅ Data preprocessing completed  
- ✅ Feature engineering completed  
- ✅ Baseline Linear Regression implemented  
- ✅ LSTM models trained and evaluated  
- ✅ Model comparison performed  
- ✅ Flask backend integrated  
- ✅ Interactive dashboard developed  
- ✅ Documentation completed  
- ✅ GitHub repository finalized  

---

## Conclusion

This project demonstrates a complete real-world machine learning lifecycle, from raw data processing to deep learning-based forecasting and deployment.  
It highlights strong understanding of time-series modeling, ML evaluation, system integration, and professional software engineering practices, making it a comprehensive and industry-ready solution for smart energy analytics.
