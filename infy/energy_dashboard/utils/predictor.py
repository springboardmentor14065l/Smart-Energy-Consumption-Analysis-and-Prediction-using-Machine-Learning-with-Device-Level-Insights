import tensorflow as tf
import os

class EnergyPredictor:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                print(f"Loading model from {self.model_path}...")
                self.model = tf.keras.models.load_model(self.model_path)
                print("Model loaded successfully.")
            else:
                print(f"Model file not found at {self.model_path}")
        except Exception as e:
            print(f"Error loading Keras model: {e}")

    def predict(self, input_data):
        """
        Wrapper for model prediction.
        """
        if self.model is None:
            print("Error: Model is not initialized.")
            return None
        
        try:
            # simple check: if input is 1D list, maybe reshape to (1, 1, features) or whatever model needs
            # This is highly dependent on the specific LSTM training shape.
            # Assuming input_data is already pre-processed for now.
            
            # Example: if model expects (batch, timesteps, features)
            # data = np.array(input_data)
            # if len(data.shape) == 1:
            #     data = np.expand_dims(data, axis=0)
            
            return self.model.predict(input_data, verbose=0)
        except Exception as e:
            print(f"Prediction error: {e}")
            return None
