import numpy as np
import pandas as pd
import os
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

class PredictionEngine:
    def __init__(self, model_path, data_path):
        self.model_path = model_path
        self.data_path = data_path
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self._initialize()

    def _initialize(self):
        # Load the model
        if os.path.exists(self.model_path):
            self.model = load_model(self.model_path)
            print(f"Model loaded from {self.model_path}")
        else:
            raise FileNotFoundError(f"Model file not found at {self.model_path}")

        # Fit the scaler using the dataset to ensure consistency
        if os.path.exists(self.data_path):
            df = pd.read_csv(self.data_path)
            if 'Energy Consumption (kWh)' in df.columns:
                energy_data = df['Energy Consumption (kWh)'].values.reshape(-1, 1)
                self.scaler.fit(energy_data)
                print("Scaler fitted using training data.")
            else:
                raise ValueError("Energy column not found in dataset for scaling.")
        else:
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")

    def predict_next_hour(self, last_24_values):
        """
        Predicts the energy consumption for the next hour.
        Args:
            last_24_values (list or np.array): The last 24 energy consumption values.
        Returns:
            float: Predicted consumption for the next hour.
        """
        if len(last_24_values) != 24:
            raise ValueError("Exactly 24 values are required for prediction.")

        # Scale the input
        scaled_input = self.scaler.transform(np.array(last_24_values).reshape(-1, 1))
        
        # Reshape for LSTM (1, 24, 1)
        lstm_input = scaled_input.reshape(1, 24, 1)
        
        # Predict
        prediction_scaled = self.model.predict(lstm_input)
        
        # Inverse transform to get actual kWh
        prediction = self.scaler.inverse_transform(prediction_scaled)
        
        return float(prediction[0][0])

if __name__ == "__main__":
    # Test with dummy data
    engine = PredictionEngine(
        model_path=r"c:\001 PROJECTS\Infosys Internship\Week 5-6\LSTM Model\lstm_energy_model.h5",
        data_path=r"c:\001 PROJECTS\Infosys Internship\Week 1-2\Ready For Feature Eng dataset\cleaned_energy_consumption_data.csv"
    )
    dummy_input = [4.5] * 24
    pred = engine.predict_next_hour(dummy_input)
    print(f"Test Prediction: {pred} kWh")
