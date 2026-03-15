import sys
import os
import pandas as pd
from unittest.mock import MagicMock

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from insight_engine import InsightEngine

def test_personalization():
    # Mock prediction engine
    mock_prediction = MagicMock()
    mock_prediction.predict_next_hour.return_value = 5.0
    
    # Create dummy df
    df = pd.DataFrame({
        'Timestamp': pd.date_range(start='2024-01-01', periods=100, freq='h'),
        'energy': [2.0] * 100,
        'Appliance Type': ['Air Conditioner'] * 100,
        'Outdoor Temperature': [32] * 100
    })
    
    # Profile A: Bill focus
    profile_a = {
        "goal": "Reduce bill",
        "peak_rate": 10.0,
        "tariff_type": "Fixed rate"
    }
    engine_a = InsightEngine(df, mock_prediction, profile_a)
    insights_a = engine_a.get_advanced_insights()
    
    # Profile B: Carbon focus
    profile_b = {
        "goal": "Reduce carbon footprint",
        "peak_rate": 10.0,
        "tariff_type": "Fixed rate"
    }
    engine_b = InsightEngine(df, mock_prediction, profile_b)
    insights_b = engine_b.get_advanced_insights()
    
    print("Profile A Insight:", insights_a[0]['text'].encode('ascii', 'ignore').decode())
    print("Profile B Insight:", insights_b[0]['text'].encode('ascii', 'ignore').decode())
    
    assert "Save money" in insights_a[0]['text']
    assert "Carbon alert" in insights_b[0]['text']
    print("Personalization Test Passed!")

if __name__ == "__main__":
    test_personalization()
