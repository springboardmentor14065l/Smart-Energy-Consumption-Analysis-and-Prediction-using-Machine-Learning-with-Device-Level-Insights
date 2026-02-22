
# 📌 Smart Home Energy Consumption Prediction

<img width="749" height="299" alt="image" src="https://github.com/user-attachments/assets/2e764280-90e3-48e7-affe-b7ce89175e10" />

<img width="753" height="352" alt="image" src="https://github.com/user-attachments/assets/3e9f1ea1-fb95-46a9-952d-98ccc9c982cf" />


## 📖 Overview

This project is an end-to-end **Machine Learning based Smart Home Energy Consumption Prediction System** developed during the **Infosys Springboard AI/ML Internship (Dec 2025 – Feb 2026)**.

The system predicts household energy consumption using historical usage patterns and time-based features. It includes:

* Data preprocessing & feature engineering
* Baseline ML models (Linear Regression, Random Forest)
* LSTM time-series model
* Model comparison
* Flask-based deployment
* Interactive dashboard interface

---

## 🎯 Problem Statement

Accurately predicting household energy consumption helps:

* Reduce electricity waste
* Optimize appliance usage
* Enable smart energy management
* Support sustainability initiatives

The goal was to build a predictive system that can forecast energy consumption based on household and environmental parameters.

---

## 🛠 Tech Stack

### 🔹 Programming & Libraries

* Python
* NumPy
* Pandas
* Matplotlib
* Seaborn
* Scikit-learn
* TensorFlow / Keras
* Flask

### 🔹 Deployment

* Flask Web Framework
* HTML, CSS
* Joblib (Model Serialization)

---

## 📊 Dataset Description

The dataset contains smart home energy consumption records including:

* Home ID
* Outdoor Temperature (°C)
* Household Size
* Hour, Day, Month, Weekday
* Appliance Type (One-hot encoded)
* Seasonal Indicators
* Energy Consumption (kWh)

Time-based features were engineered to improve prediction accuracy.

---

## ⚙️ Feature Engineering

* Extracted Hour, Day, Month, Weekday
* Created Seasonal features (Spring, Summer, Winter)
* Applied One-Hot Encoding to Appliance Types
* Scaled numerical features
* Removed unnecessary columns (Timestamp, Time)

For LSTM:

* Converted data into sequential format
* Used 24-hour sliding window
* Final LSTM input shape: `(80003, 24, 19)`

---

## 🤖 Models Implemented

### 1️⃣ Linear Regression (Baseline)

* Simple and interpretable model
* R² ≈ 0.66

### 2️⃣ Random Forest Regressor

* Ensemble learning method
* Slightly lower performance than Linear Regression

### 3️⃣ LSTM (Time Series Model)

* Designed for sequential data
* Used 24-hour time steps
* Evaluated using MAE, RMSE, and R²

---

## 📈 Model Comparison

| Model             | MAE          | RMSE     | R² Score         |
| ----------------- | ------------ | -------- | ---------------- |
| Linear Regression | ~0.41        | ~0.49    | ~0.66            |
| Random Forest     | ~0.41        | ~0.50    | ~0.64            |
| LSTM              | Higher error | Lower R² | Weak performance |

✅ **Final Selected Model: Linear Regression**

Reason:

* Best R² score
* Lower error
* Stable performance
* Lightweight for deployment

---

## 🌐 Deployment

The best model was saved using:

```python
joblib.dump(lr_model, "best_energy_model.pkl")
```

A Flask application was developed to:

* Accept user inputs
* Recreate feature structure
* Generate predictions
* Provide energy usage suggestions

---

## 🖥 Web Application Features

* User-friendly interface
* Energy consumption prediction
* Smart suggestion system:

  * High consumption warning
  * Efficient usage detection
  * Moderate usage monitoring advice

---

## 📊 Dashboard & Visualization

The system includes:

* Hourly energy trends
* Monthly usage patterns
* Appliance-wise distribution
* Model performance comparison charts
* LSTM training vs validation loss graph

---

## 🚀 How to Run Locally

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/smart-energy-prediction.git
cd smart-energy-prediction
```

### 2️⃣ Install Requirements

```bash
pip install -r requirements.txt
```

### 3️⃣ Run Flask App

```bash
python app.py
```

Visit:

```
http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
Smart_Home_Energy_Prediction/
│
├── app.py
├── best_energy_model.pkl
├── requirements.txt
├── README.md
│
├── templates/
│   └── index.html
│
├── static/
│   └── styles.css
│
└── notebooks/
    └── model_training.ipynb
```

---

## 📌 Key Learnings

* Real-world ML pipeline implementation
* Feature engineering for time-series data
* Model evaluation & comparison
* Sequential modeling using LSTM
* Production deployment using Flask
* Handling feature consistency between training and inference

---

## 🔮 Future Improvements

* Hyperparameter tuning for LSTM
* Real-time energy monitoring
* Cloud deployment
* Integration with IoT devices
* Advanced deep learning architectures

---

## 👨‍💻 Author

**Swapnil Pal**
B.Tech Computer Science & Business Systems
SVKM’s NMIMS MPSTME

📧 Email: [palswapnil629@gmail.com](mailto:palswapnil629@gmail.com)
🔗 LinkedIn: [https://www.linkedin.com/in/swapnil-pal-394124276](https://www.linkedin.com/in/swapnil-pal-394124276)
💻 GitHub: [https://github.com/Swapnill435](https://github.com/Swapnill435)

---

## 📜 Internship Details

**AI/ML Internship – Infosys Springboard**
Dec 2025 – Feb 2026

Developed an end-to-end Smart Home Energy Prediction system including model training, evaluation, dashboard visualization, and Flask-based deployment.

---

# ⭐ Final Summary

This project demonstrates a complete machine learning lifecycle:

> Data → Feature Engineering → Modeling → Evaluation → Deployment → Web Integration



Tell me what level you want 🔥

