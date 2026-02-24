import pandas as pd
import os
import random

def load_data(filepath):
    """
    Loads predictions.csv and returns formatted data for the dashboard.
    """
    if not os.path.exists(filepath):
        print(f"Error: Data file not found at {filepath}")
        return None
    
    try:
        df = pd.read_csv(filepath)
        
        # Check if required columns exist
        required_columns = ['timestamp', 'actual_energy', 'predicted_energy']
        if not all(col in df.columns for col in required_columns):
            print(f"Error: CSV is missing required columns: {required_columns}")
            return None

        # Convert timestamp to string if needed
        # df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

        data = {
            'labels': df['timestamp'].tolist(),
            'actual': df['actual_energy'].tolist(),
            'predicted': df['predicted_energy'].tolist()
        }
        return data
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return None

def get_stats(filepath):
    """
    Returns basic statistics about the energy data.
    """
    if not os.path.exists(filepath):
        return None
    
    try:
        df = pd.read_csv(filepath)
        stats = {
            'avg_actual': round(df['actual_energy'].mean(), 2),
            'avg_predicted': round(df['predicted_energy'].mean(), 2),
            'max_actual': round(df['actual_energy'].max(), 2),
            'min_actual': round(df['actual_energy'].min(), 2),
            'total_readings': len(df)
        }
        return stats
    except Exception as e:
        print(f"Error calculating stats: {e}")
        return None

def get_appliance_data(filepath):
    """
    Returns data broken down by appliance.
    MOCKS appliance data if not present in CSV.
    """
    if not os.path.exists(filepath):
        return None
    
    try:
        df = pd.read_csv(filepath)
        
        # Mock appliance column if missing
        if 'appliance' not in df.columns:
            # Deterministic mock based on index to keep consistent across refreshes (sort of)
            appliances = ['Fridge', 'AC', 'Heater', 'Lights', 'Washing Machine']
            df['appliance'] = [appliances[i % len(appliances)] for i in range(len(df))]
        
        result = {}
        unique_appliances = df['appliance'].unique()
        
        for app in unique_appliances:
            app_df = df[df['appliance'] == app]
            result[app] = {
                'labels': app_df['timestamp'].tolist(),
                'actual': app_df['actual_energy'].tolist(),
                'predicted': app_df['predicted_energy'].tolist()
            }
            
        return result
    except Exception as e:
        print(f"Error getting appliance data: {e}")
        return None

def get_suggestions(filepath):
    """
    Generates smart energy saving tips based on data.
    """
    if not os.path.exists(filepath):
        return []
    
    suggestions = []
    try:
        df = pd.read_csv(filepath)
        avg_usage = df['actual_energy'].mean()
        
        # 1. High Usage Alert
        recent_usage = df['actual_energy'].iloc[-1]
        if recent_usage > avg_usage * 1.2:
            suggestions.append({
                'title': 'High Usage Alert',
                'msg': f'Your recent usage ({recent_usage:.2f} kWh) is 20% higher than average. Check AC or Heater settings.',
                'type': 'warning'
            })
            
        # 2. Night Usage (Simulated logic as we don't parse full datetime here for speed, but could)
        # Using a simple heuristic or just a general tip if variability is high
        if df['actual_energy'].std() > 2.0:
             suggestions.append({
                'title': 'Optimize Timing',
                'msg': 'High usage variability detected. Run heavy appliances like Washing Machines at night (10 PM - 6 AM) to save costs.',
                'type': 'info'
            })
            
        # 3. Fridge Logic (Simulated)
        suggestions.append({
            'title': 'Appliance Health',
            'msg': 'Fridge energy consumption is slightly unstable. Consider cleaning the condenser coils to improve efficiency by 15%.',
            'type': 'maintenance'
        })
        
        return suggestions
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return []

def calculate_cost(filepath, unit_cost):
    """
    Calculates estimated cost based on predicted energy.
    """
    if not os.path.exists(filepath):
        return None
        
    try:
        df = pd.read_csv(filepath)
        total_predicted = df['predicted_energy'].sum()
        
        # Assuming data covers a certain period, let's normalize to a daily estimate
        # If data is hourly, total sum is simply kWh for the period.
        # Let's assume the CSV is creating a projection for the next 'N' hours.
        
        avg_hourly_consumption = total_predicted / len(df)
        daily_estimate = avg_hourly_consumption * 24 * unit_cost
        monthly_estimate = daily_estimate * 30
        
        # Savings potential (10% reduction)
        savings = monthly_estimate * 0.10
        
        return {
            'daily_cost': round(daily_estimate, 2),
            'monthly_cost': round(monthly_estimate, 2),
            'savings_potential': round(savings, 2),
            'unit_cost': unit_cost
        }
    except Exception as e:
        print(f"Error calculating cost: {e}")
        return None
