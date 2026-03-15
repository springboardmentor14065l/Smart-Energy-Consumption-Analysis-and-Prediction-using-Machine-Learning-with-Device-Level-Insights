# Final Project Report: Smart Energy Consumption Analysis and Prediction

## Project Overview
The goal of this project was to develop an intelligent system for monitoring house-level energy consumption and providing future usage predictions using Machine Learning (LSTM). The system provides device-level insights and energy efficiency recommendations through an interactive web dashboard.

## System Architecture
The system is built with a decoupled architecture focusing on scalability and performance:
1. **Data Layer**: Cleaned and preprocessed energy consumption data (univariate and multivariate).
2. **ML Model Layer**: Multi-layer LSTM network trained on time-series data to predict next-hour energy demand.
3. **API Backend**: Flask-based RESTful API that bridges the frontend and the ML model.
4. **Visualization Engine**: Matplotlib/Seaborn integration for generating on-demand consumption analytics.
5. **Web Dashboard**: Interactive user interface built with HTML5, CSS3 (Glassmorphism), and Vanilla JavaScript.

## Module Implementation Summary

### Module 7: Dashboard and Visualization
- **Hourly/Daily/Weekly Trends**: Implemented time-series visualizations to track consumption patterns.
- **Appliance Breakdown**: Developed device-wise usage distribution analysis using pie charts.
- **Dynamic Chart Generation**: Visualization engine generates charts directly from the source dataset for real-time accuracy.

### Module 8: Web Application and Prediction
- **Flask API**: Developed robust endpoints for statistics, predictions, and suggestions.
- **LSTM Integration**: Integrated the `.h5` model with a real-time prediction pipeline.
- **Smart Suggestions**: Implemented a rule-based engine to provide actionable energy efficiency tips to users.

## Testing and Results
- **Model Accuracy**: The LSTM model achieved high accuracy on the test set with low Mean Absolute Error (MAE).
- **Frontend Performance**: Dashboard loads in under 2 seconds, and charts refresh dynamically upon user interaction.
- **API Reliability**: Standard API tests confirm correct JSON responses and error handling for prediction requests.

## Conclusion
The Smart Energy Consumption system successfully integrates advanced deep learning models with a modern web interface. It empowers users to understand their consumption habits and proactively manage their energy footprint through accurate forecasts and smart suggestions.
