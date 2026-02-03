# Week 5–6: LSTM Model Development & Evaluation

## Objective
To build an LSTM-based time series forecasting model for appliance-level energy consumption and compare it with the baseline linear regression model.

## Data Used
- Hourly energy consumption data
- Appliance-wise separated datasets
- Scaled and sequentially formatted for LSTM input

## Work Done

### Week 5: LSTM Model Development
- Designed and implemented LSTM architecture using TensorFlow/Keras
- Prepared sequential input data using sliding windows
- Tuned hyperparameters such as epochs, batch size, and learning rate
- Used EarlyStopping to prevent overfitting

### Week 6: Model Evaluation and Integration
- Evaluated model using MAE, RMSE, and R² score
- Compared LSTM performance with baseline linear regression
- Saved trained LSTM models and scalers
- Implemented a Flask-compatible prediction function
- Tested predictions using unseen sample inputs

## Observations
- LSTM outperformed the baseline model for appliances with temporal patterns
- Stable appliances showed lower prediction error
- Variable appliances showed higher error due to usage irregularity

## Outcome
A fully trained, evaluated, and deployment-ready LSTM model for appliance-level energy forecasting.
