import sys
import os
import pandas as pd
from unittest.mock import MagicMock

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from insight_engine import InsightEngine

def test_billing_scaling():
    # 24 hours * 2 kWh each = 48 kWh per day
    # 30 days * 48 kWh = 1440 kWh per month
    # Scaled by 0.20 = 288 kWh per month
    # Rate of 10 Rs = 2880 Rs (realistic range)
    
    df = pd.DataFrame({
        'Timestamp': pd.date_range(start='2024-01-01', periods=720, freq='h'),
        'Energy Consumption (kWh)': [2.0] * 720,
        'Appliance Type': ['Heater'] * 720,
        'Home ID': [1] * 720
    })
    
    mock_prediction = MagicMock()
    profile = {"home_id": 1, "peak_rate": 15.0, "tariff_type": "Fixed rate"}
    
    engine = InsightEngine(df, mock_prediction, profile)
    # The internal df is already scaled
    bill = engine._estimate_bill()
    
    print(f"Internal Total kWh: {bill['total_kwh']}")
    print(f"Projected Bill: {bill['projected']}")
    
    # 1440 * 0.2 = 288.0 kWh
    assert bill['total_kwh'] == 288.0
    # 288 * 15 = 4320.0 Rs
    assert 4000 <= bill['projected'] <= 6000
    print("Billing Scaling Test Passed!")

if __name__ == "__main__":
    test_billing_scaling()
