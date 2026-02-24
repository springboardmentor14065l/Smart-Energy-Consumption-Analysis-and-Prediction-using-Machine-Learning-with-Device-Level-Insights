from flask import Flask, render_template, jsonify, request
import sys
import os
import numpy as np

# Ensure utils is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import load_data, get_stats
from utils.predictor import EnergyPredictor

app = Flask(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'predictions.csv')
MODEL_FILE = os.path.join(BASE_DIR, 'model', 'best_lstm_energy_model.keras')

# Initialize components (Model loaded once at startup)
# We wrap this in a try-except block to prevent crash if model is missing during dev
try:
    predictor = EnergyPredictor(MODEL_FILE)
    print("System: Model initialized successfully.")
except Exception as e:
    print(f"System: Warning - Model initialization failed: {e}")
    predictor = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def api_data():
    """
    Returns historical and predicted data from CSV.
    """
    data = load_data(DATA_FILE)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Failed to load data'}), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """
    Returns statistical summary of the energy data.
    """
    stats = get_stats(DATA_FILE)
    if stats:
        return jsonify(stats)
    return jsonify({'error': 'Failed to load stats'}), 500

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    Real-time prediction endpoint.
    Expected JSON input: {'features': [val1, val2, ...]} (shape corresponding to model input)
    """
    if not predictor or not predictor.model:
        return jsonify({'error': 'Model not loaded'}), 503

    try:
        content = request.json
        if not content or 'features' not in content:
            return jsonify({'error': 'Invalid input, "features" key required'}), 400
        
        features = np.array(content['features'])
        
        # Basic reshaping if needed - assuming model expects (1, n_steps, n_features) or similar
        # For now, passing raw features to predictor which handles specific logic
        prediction = predictor.predict(features)
        
        if prediction is not None:
            # Convert numpy types to python native types for JSON serialization
            result = prediction.tolist() if isinstance(prediction, np.ndarray) else prediction
            return jsonify({'prediction': result})
        else:
            return jsonify({'error': 'Prediction failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check
@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'model_loaded': predictor is not None and predictor.model is not None,
        'data_accessible': os.path.exists(DATA_FILE)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
