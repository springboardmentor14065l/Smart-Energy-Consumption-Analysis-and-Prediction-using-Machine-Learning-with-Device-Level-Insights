from flask import Flask, render_template, jsonify, send_from_directory, request
import os
import random
import json
from prediction_engine import PredictionEngine
from visualization import Visualizer
from insight_engine import InsightEngine
from db_manager import DatabaseManager

app = Flask(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(os.path.dirname(BASE_DIR), "Week 5-6", "LSTM Model", "lstm_energy_model.h5")
DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), "Week 1-2", "Ready For Feature Eng dataset", "cleaned_energy_consumption_data.csv")
IMAGES_DIR = os.path.join(BASE_DIR, "static", "images")

# Initialize DB, Engine, Visualizer
db = DatabaseManager()
engine = PredictionEngine(MODEL_PATH, DATA_PATH)
visualizer = Visualizer(DATA_PATH, IMAGES_DIR)

# Load user profile for InsightEngine
user_profile = db.get_user_profile(1)
insight_engine = InsightEngine(visualizer.df, engine, user_profile)

@app.route('/')
def dashboard():
    # Check if user is onboarded (has a record in user_preferences)
    is_onboarded = db.get_user_profile(1) is not None
    return render_template('index.html', is_onboarded=is_onboarded)

@app.route('/api/onboarding', methods=['POST'])
def save_onboarding():
    data = request.json
    try:
        db.save_user_profile(data)
        # Re-init insight engine with new profile
        global insight_engine
        updated_profile = db.get_user_profile(1)
        insight_engine = InsightEngine(visualizer.df, engine, updated_profile)
        
        return jsonify({'status': 'success', 'message': 'Profile saved successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/profile', methods=['GET'])
def get_profile():
    profile = db.get_user_profile(1)
    if profile:
        return jsonify({'status': 'success', 'profile': profile})
    return jsonify({'status': 'error', 'message': 'Profile not found'}), 404

@app.route('/api/personalized-insights', methods=['GET'])
def get_personalized():
    try:
        # Refresh profile from DB to ensure persistence after refresh
        profile = db.get_user_profile(1)
        if profile:
            insight_engine.user_profile = profile
            # Also need to re-filter data if home_id changed
            home_id = int(profile.get('home_id', 1))
            insight_engine.df = insight_engine.df_raw[insight_engine.df_raw['home_id'] == home_id].copy()
            insight_engine.df['energy'] = insight_engine.df['energy'] * 0.20
            
        # Get full personalized payload
        data = insight_engine.get_personalized_insights()
        return jsonify({
            'status': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    try:
        # For demo, just clear preference but keep user
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_preferences WHERE user_id = 1")
            conn.commit()
        
        # Reset engine to defaults
        global insight_engine
        insight_engine = InsightEngine(visualizer.df, engine, None)
        
        return jsonify({'status': 'success', 'message': 'Logged out completed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/predict', methods=['GET'])
def get_prediction():
    # Use user-specific filtered and scaled data
    df = insight_engine.df
    if df.empty:
        return jsonify({'status': 'error', 'message': 'No data available'}), 404
        
    last_24 = df.sort_values('timestamp').tail(24)['energy'].tolist()
    
    try:
        prediction = engine.predict_next_hour(last_24)
        return jsonify({
            'status': 'success',
            'prediction': round(prediction, 3),
            'unit': 'kWh'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    try:
        # Use the same dynamic logic as personalized insights
        insights = insight_engine.get_personalized_insights()
        recommendations = insights['suggestions']
        
        # Format for output (compatibility with existing frontend if any remains)
        suggestions_text = [item['title'] for item in recommendations]
        
        return jsonify({
            'status': 'success',
            'suggestions': suggestions_text[:3], 
            'metadata': recommendations 
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/data', methods=['GET'])
def get_chart_data():
    df = insight_engine.df
    # Hourly data (Last 24 hours)
    recent_24 = df.sort_values('timestamp').tail(24)
    hourly_labels = recent_24['timestamp'].dt.strftime('%H:%M').tolist()
    hourly_values = recent_24['energy'].tolist()

    # Daily data (Last 7 days)
    daily = df.groupby(df['timestamp'].dt.date)['energy'].sum().tail(7)
    daily_labels = [d.strftime('%Y-%m-%d') for d in daily.index]
    daily_values = daily.tolist()

    # Device data
    device_usage = df.groupby('appliance')['energy'].sum()
    device_labels = device_usage.index.tolist()
    device_values = device_usage.tolist()

    return jsonify({
        'hourly': {'labels': hourly_labels, 'values': hourly_values},
        'daily': {'labels': daily_labels, 'values': daily_values},
        'devices': {'labels': device_labels, 'values': device_values}
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    df = insight_engine.df
    total_consumption = df['energy'].sum()
    avg_hourly = df['energy'].mean()
    max_usage = df['energy'].max()
    
    return jsonify({
        'total_consumption': round(total_consumption, 2),
        'avg_hourly': round(avg_hourly, 2),
        'max_usage': round(max_usage, 2)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
