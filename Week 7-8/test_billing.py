import sys
import os
import pandas as pd
from unittest.mock import MagicMock

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from insight_engine import InsightEngine

def test_billing():
    df = pd.DataFrame({
        'Timestamp': pd.to_datetime(['2024-01-01 08:00:00', '2024-01-01 20:00:00']),
        'energy': [10.0, 10.0],
        'Appliance Type': ['Heater', 'Lights']
    })
    
    mock_prediction = MagicMock()
    
    # 1. Fixed Rate
    profile_fixed = {"tariff_type": "Fixed rate", "peak_rate": 5.0}
    engine_fixed = InsightEngine(df, mock_prediction, profile_fixed)
    bill_fixed = engine_fixed._estimate_bill(df)
    
    # Expected current: (10*5) + (10*5) = 100
    assert bill_fixed['current'] == 100.0
    
    # 2. Time of Use
    # Peak: 6-10 AM and 6-10 PM
    profile_tou = {
        "tariff_type": "Time-of-use", 
        "peak_rate": 10.0, 
        "off_peak_rate": 5.0
    }
    engine_tou = InsightEngine(df, mock_prediction, profile_tou)
    bill_tou = engine_tou._estimate_bill(df)
    
    # 8 AM is peak (10 * 10 = 100)
    # 8 PM is peak (10 * 10 = 100)
    assert bill_tou['current'] == 200.0
    
    print("Billing Test Passed!")

if __name__ == "__main__":
    test_billing()
