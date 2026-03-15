# Smart Energy Consumption Analysis and Prediction

A comprehensive machine learning project designed to analyze appliance-level energy consumption, predict future demand, and provide personalized insights to help users achieve their energy goals.

## Project Overview
This repository contains the full development cycle of a Smart Energy Advisor, from initial data exploration and preprocessing to a sophisticated, real-time dashboard powered by machine learning (LSTM).

### Key Features
- **Advanced Analytics**: Insights into daily, hourly, and device-level energy usage.
- **ML Demand Forecasting**: Uses a Deep Learning (LSTM) model to predict the next hour's energy consumption with high accuracy.
- **Goal-Driven Advisor**: Tailored energy-saving suggestions based on user goals:
  - **Reduce Bills**: Practical tips to lower monthly electricity costs.
  - **Carbon Footprint**: Environmental impact tracking and CO2 reduction advice.
  - **Avoid Peak Charges**: Load-shifting strategies for time-of-use tariffs.
  - **General Monitoring**: Overall system health and efficiency scores.
- **Premium Dashboard**: A stunning, glassmorphism-inspired UI with interactive charts and real-time alerts.

## 🛠 Tech Stack
- **Backend**: Python, Flask
- **Frontend**: HTML5, Vanilla CSS (Glassmorphism), JavaScript (main.js)
- **Machine Learning**: TensorFlow/Keras (LSTM), Scikit-Learn, Pandas, NumPy
- **Visualizations**: Chart.js, Matplotlib (for static reports)
- **Database**: SQLite (for profile and consumption management)

## 📂 Project Structure
- `Week 1-2/`: Data identification, initial preprocessing, and exploratory analysis.
- `Week 3-4/`: Feature engineering and baseline model development.
- `Week 5-6/`: Deep learning (LSTM) implementation and training.
- `Week 7-8/`: Premium dashboard development, integration of the "Smart Energy Advisor," and final testing.
- `All Documentation/`: Detailed reports (PDF/TXT) covering each phase of the internship.

## Getting Started

### 1. Prerequisites
- Python 3.8+
- Virtual Environment (recommended)

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/Kavanareddym/Smart-Energy-Consumption-Analysis-and-Prediction-using-Machine-Learning-with-Device-Level-Insights.git
cd Smart-Energy-Consumption-Analysis-and-Prediction

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r "Week 7-8/requirements.txt"
```

### 3. Run the Dashboard
```bash
python "Week 7-8/app.py"
```
Visit `http://localhost:5000` to interact with the Smart Energy Advisor.

## 👤 Author
**Kavana Reddy M**
*Infosys Internship Project*

---
*Note: This project was developed as part of an intensive internship program focusing on Machine Learning and Device-Level Energy Insights.*
