import pandas as pd
import numpy as np
from insight_engine import InsightEngine

class MockPredictionEngine:
    def predict_next_hour(self, last_24):
        # Predict a spike
        return last_24[-1] + 1.0

def test_bespoke_insights():
    # Create mock data with a clear story:
    # 1. AC is the top appliance
    # 2. Outdoor temp is high
    # 3. Overall average is high
    data = {
        'Timestamp': pd.date_range(start='2023-01-01', periods=100, freq='H'),
        'Appliance Type': ['Air Conditioning'] * 60 + ['Lighting'] * 40,
        'energy': [3.0] * 60 + [0.5] * 40,
        'Outdoor Temperature': [32.0] * 100
    }
    df = pd.DataFrame(data)
    
    pred_engine = MockPredictionEngine()
    insight_engine = InsightEngine(df, pred_engine)
    
    insights = insight_engine.get_advanced_insights()
    
    print("\n--- Generated Tailor-Made Insights ---")
    for i in insights:
        print(f"[{i['type'].upper()}] ({i['level']}): {i['text']}")
    
    # Assertions
    types = [i['type'] for i in insights]
    assert 'predictive' in types
    assert 'efficiency' in types
    assert 'target' in types
    assert 'environmental' in types
    
    print("\nTest Passed: All bespoke insight categories were correctly triggered by the mock data.")

if __name__ == "__main__":
    test_bespoke_insights()
