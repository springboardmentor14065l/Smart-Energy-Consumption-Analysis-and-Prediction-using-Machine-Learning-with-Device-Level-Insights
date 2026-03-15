import pandas as pd
from insight_engine import InsightEngine

def test_goals():
    # Mock profile
    profile = {
        'id': 1,
        'home_id': 1,
        'tariff_type': 'Time-of-use',
        'peak_rate': 7.0,
        'off_peak_rate': 4.5,
        'goal': 'Reduce bill'
    }
    
    # Initialize engine with mock data
    df = pd.DataFrame([{
        'timestamp': pd.Timestamp.now(),
        'home_id': 1,
        'appliance': 'Heater',
        'energy': 2.0,
        'temperature': 20
    }])
    
    engine = InsightEngine(df, profile)
    
    # Test 1: Reduce Bill
    print("\n--- Testing Goal: Reduce Bill ---")
    insights = engine.get_personalized_insights()
    print(f"Summary: {insights['goal_summary']}")
    for s in insights['suggestions']:
        print(f"  [{s['priority']}] {s['title']} - {s['impact']}")

    # Test 2: Reduce Carbon Footprint
    print("\n--- Testing Goal: Reduce carbon footprint ---")
    engine.user_profile['goal'] = 'Reduce carbon footprint'
    insights = engine.get_personalized_insights()
    print(f"Summary: {insights['goal_summary']}")
    for s in insights['suggestions']:
        print(f"  [{s['priority']}] {s['title']} - {s['impact']}")

    # Test 3: Avoid Peak Charges
    print("\n--- Testing Goal: Avoid peak charges ---")
    engine.user_profile['goal'] = 'Avoid peak charges'
    insights = engine.get_personalized_insights()
    print(f"Summary: {insights['goal_summary']}")
    for s in insights['suggestions']:
        print(f"  {s['title']} - {s['impact']}")
    if insights['alerts']:
        print(f"  Alert: {insights['alerts'][0]['title']}")

    # Test 4: General Monitoring
    print("\n--- Testing Goal: General monitoring ---")
    engine.user_profile['goal'] = 'General monitoring'
    insights = engine.get_personalized_insights()
    print(f"Summary: {insights['goal_summary']}")
    for s in insights['suggestions']:
        print(f"  {s['title']} - {s['impact']}")

if __name__ == "__main__":
    test_goals()
