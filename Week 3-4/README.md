# Week 3-4: Feature Engineering and Data Processing

## Overview
This phase involved transforming the cleaned data into a format suitable for machine learning models, specifically focusing on appliance-level insights.

## Key Activities
- **Feature Engineering**: Engineered new features from the raw telemetry and environmental data to improve predictive accuracy.
- **Appliance-Level Splitting**: Processed data for individual appliances (Air Conditioning, Computer, Dishwasher, etc.).
- **Data Scaling and Train-Test Split**: Automated the process of scaling features and splitting data per appliance into training and testing sets.
- **Automated Workflow**: Developed a structured approach to generate CSV files for each appliance's model input.

## Files
- `1. Feature Eng/Feature_engineering.ipynb`: Notebook containing the feature engineering and data splitting logic.
- `1. Feature Eng/processed_appliance_data/`: Directory containing the processed `X_train`, `X_test`, `y_train`, and `y_test` files for all appliances.
