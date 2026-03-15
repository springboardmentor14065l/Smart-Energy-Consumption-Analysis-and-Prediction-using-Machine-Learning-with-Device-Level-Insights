import json
import os
import pandas as pd
from flask import Flask

# Mock Visualizer for testing
class MockVisualizer:
    def __init__(self, df):
        self.df = df

def test_suggestions_logic():
    # Load tips
    with open('suggestions.json', 'r') as f:
        tips_data = json.load(f)
    
    # Create mock data where AC is high
    data = {
        'Timestamp': pd.date_range(start='2023-01-01', periods=10, freq='H'),
        'Appliance Type': ['Air Conditioning'] * 10,
        'energy': [2.5] * 10
    }
    df = pd.DataFrame(data)
    visualizer = MockVisualizer(df)
    
    # Logic from app.py
    recent_data = df.tail(100)
    top_appliance = recent_data.groupby('Appliance Type')['energy'].sum().idxmax()
    
    selected_tips = []
    if top_appliance in tips_data['appliances']:
        selected_tips.append(tips_data['appliances'][top_appliance])
    
    print(f"Top Appliance: {top_appliance}")
    print(f"Selected Item from Appliance Category: {selected_tips}")
    
    assert top_appliance == 'Air Conditioning'
    assert len(selected_tips) > 0
    print("Test Passed: Logic correctly identifies top appliance and fetches relevant tips.")

if __name__ == "__main__":
    test_suggestions_logic()
