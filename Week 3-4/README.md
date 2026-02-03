Overview

This project predicts energy consumption using a simple Linear Regression model.

## Dataset

    The dataset contains:

         timestamp – date and time
         device – appliance name
         energy – energy used (kWh)

## Data Cleaning

     Converted timestamp to datetime
     Removed missing values
     Removed duplicate records
     Extracted hour from timestamp

## Features Used

     hour – hour of the day
     device_code – numeric value for each device

## Model Used

     Linear Regression
     Train-test split: 70% training, 30% testing