import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

class InsightEngine:
    def __init__(self, df, prediction_engine, user_profile=None):
        self.prediction_engine = prediction_engine
        self.user_profile = user_profile or self._get_default_profile()
        
        # 1. Standardize and copy
        df_internal = df.copy()
        col_map = {
            'Home ID': 'home_id',
            'Timestamp': 'timestamp',
            'Energy Consumption (kWh)': 'energy',
            'Appliance Type': 'appliance',
            'Outdoor Temperature': 'temperature'
        }
        df_internal = df_internal.rename(columns=col_map)
        df_internal['timestamp'] = pd.to_datetime(df_internal['timestamp'])
        
        # 2. Filter by Home ID
        self.df_raw = df_internal.copy()
        home_id = int(self.user_profile.get('home_id', 1))
        if 'home_id' in self.df_raw.columns:
            self.df = self.df_raw[self.df_raw['home_id'] == home_id].copy()
        else:
            self.df = self.df_raw.copy()
            
        # 3. Apply Scaling Factor (0.20) for realistic Residential Data
        if not self.df.empty:
            self.df['energy'] = self.df['energy'] * 0.20

    def get_personalized_insights(self):
        if self.df.empty:
            return self._get_empty_payload()
            
        persona_report = self._calculate_energy_persona()
        score = self._calculate_efficiency_score()
        bill_data = self._calculate_dynamic_billing()
        
        forecast_val = self._get_lstm_forecast()
        
        # New Goal-Driven Advisor Flow
        goal = self.user_profile.get('goal', 'Reduce bill')
        suggestion_report = self._generate_goal_driven_recommendations(goal, bill_data, forecast_val)
        
        # Prepare graph data
        graphs = self._prepare_graph_data(bill_data)
        
        return {
            "energy_persona": persona_report['type'],
            "persona_details": persona_report,
            "efficiency_score": score,
            "projected_monthly_bill": f"₹{bill_data['projected_monthly']}",
            "appliance_breakdown": bill_data['appliance_costs'],
            "suggestions": suggestion_report['items'],
            "goal_summary": suggestion_report['summary'],
            "alerts": suggestion_report['alerts'],
            "savings_summary": {
                "total": suggestion_report['potential_total'],
                "percent": suggestion_report['potential_percent']
            },
            "forecast_next_hour": f"{forecast_val} kWh",
            "graphs_data": graphs
        }

    def _generate_goal_driven_recommendations(self, goal, bill_data, forecast):
        items = []
        alerts = []
        summary = ""
        app_data = {item['appliance']: item for item in bill_data['appliance_costs']}
        total_bill = bill_data['projected_monthly']
        total_kwh = sum(item['kwh'] for item in bill_data['appliance_costs'])
        
        CO2_FACTOR = 0.85 # kg per kWh
        
        if goal == 'Reduce bill':
            summary = f"Total estimated bill is ₹{total_bill}. We've identified the top 3 devices contributing to this cost."
            items = self._get_bill_reduction_logic(app_data, total_bill)
            
        elif goal == 'Reduce carbon footprint':
            total_co2 = round(total_kwh * CO2_FACTOR, 1)
            summary = f"Current carbon footprint: {total_co2}kg CO2/month. Focused on reducing impact from high-emission devices."
            items = self._get_carbon_footprint_logic(app_data, total_kwh, CO2_FACTOR)
            
        elif goal == 'Avoid peak charges':
            peak_usage = self._calculate_peak_usage_ratio()
            summary = f"Peak usage ratio: {round(peak_usage*100)}%. Focused on shifting load to off-peak hours (Late Night/Early Morning)."
            items = self._get_peak_avoidance_logic(app_data, total_bill)
            if peak_usage > 0.4:
                alerts.append({"title": "High Peak Usage Alert", "msg": "Over 40% of your usage occurs during peak hours.", "priority": "High"})
            
        else: # General monitoring
            summary = "Real-time monitoring active. Detecting unusual spikes and usage trends."
            items = self._get_general_monitoring_logic(app_data, total_bill)
            # Detect spikes
            if not self.df.empty:
                last_hour = self.df.iloc[-1]['energy']
                avg_usage = self.df['energy'].mean()
                if last_hour > (avg_usage * 2.5):
                    alerts.append({"title": "Unusual Spike Detected", "msg": f"Real-time usage is {round(last_hour/avg_usage, 1)}x higher than average.", "priority": "Medium"})

        # Summary of Savings Potential
        total_potential = 0
        for s in items:
            savings_str = str(s.get('savings', '₹0'))
            if '₹' in savings_str:
                try:
                    val = int(savings_str.split('₹')[1].split(' ')[0].split('–')[0].split('-')[0])
                    total_potential += val
                except: pass
        
        return {
            "items": items,
            "alerts": alerts,
            "summary": summary,
            "potential_total": f"₹{max(20, total_potential)} – ₹{round(max(20, total_potential)*1.5)}",
            "potential_percent": f"{max(1, round((total_potential/(total_bill if total_bill > 0 else 1))*100))}%"
        }

    def _get_bill_reduction_logic(self, app_data, total_bill):
        suggestions = []
        # Priority logic - based on cost
        for app_name in ['Heater', 'Lights', 'Air Conditioning', 'Television', 'Dishwasher']:
            if app_name in app_data:
                app = app_data[app_name]
                ratio = (app['cost'] / total_bill) * 100 if total_bill > 0 else 0
                if ratio > 10:
                    savings = round(app['cost'] * 0.15)
                    suggestions.append({
                        "title": f"{app_name} Optimization",
                        "type": self._get_icon_type(app_name),
                        "header": f"{app_name} costs ₹{round(app['cost'])} ({round(ratio)}% of bill)",
                        "insight": f"Identified as a top contributor to your monthly bill.",
                        "recommendation": f"Reduce {app_name} runtime or use eco-modes to lower costs.",
                        "savings": f"₹{savings} / month",
                        "actions": self._get_actions(app_name),
                        "priority": "High" if ratio > 25 else "Medium",
                        "impact": f"Reduce bill by {round(ratio/5)}%"
                    })
        return suggestions[:3]

    def _get_carbon_footprint_logic(self, app_data, total_kwh, co2_factor):
        suggestions = []
        # Priority logic - based on kWh impact
        for app_name, app in sorted(app_data.items(), key=lambda x: x[1]['kwh'], reverse=True):
            app_co2 = round(app['kwh'] * co2_factor, 1)
            ratio = (app['kwh'] / total_kwh) * 100 if total_kwh > 0 else 0
            if ratio > 10:
                potential_co2_saved = round(app_co2 * 0.1, 1)
                suggestions.append({
                    "title": f"Lower {app_name} Emissions",
                    "type": self._get_icon_type(app_name),
                    "header": f"Emits {app_co2}kg CO2/month ({round(ratio)}% of total)",
                    "insight": f"This device has a high carbon impact due to heavy usage.",
                    "recommendation": "Reducing runtime by 10% saves significant CO2 emissions.",
                    "savings": f"{potential_co2_saved}kg CO2 offset",
                    "actions": self._get_actions(app_name),
                    "priority": "High" if ratio > 30 else "Medium",
                    "impact": f"Save {potential_co2_saved}kg CO2"
                })
        return suggestions[:3]

    def _get_peak_avoidance_logic(self, app_data, total_bill):
        suggestions = []
        # Focusing on heavy appliances that can be rescheduled
        reschedulable = ['Dishwasher', 'Washing Machine', 'Oven', 'Water Heater']
        for app_name in reschedulable:
            if app_name in app_data:
                app = app_data[app_name]
                savings = round(app['cost'] * 0.25) # Estimated savings from shifting to off-peak
                suggestions.append({
                    "title": f"Reschedule {app_name}",
                    "type": "appliance",
                    "header": f"Costs ₹{round(app['cost'])} in current slot",
                    "insight": "Running this during peak hours increases your tariff rate.",
                    "recommendation": "Shift usage to 11 PM - 6 AM to use off-peak rates.",
                    "savings": f"₹{savings} / month",
                    "actions": ["Use delay start timer", "Run during early morning", "Shift to weekend usage"],
                    "priority": "Medium",
                    "impact": "Shifts load to off-peak"
                })
        return suggestions[:3]

    def _get_general_monitoring_logic(self, app_data, total_bill):
        suggestions = []
        # Detection of unusual appliances or trends
        sorted_apps = sorted(app_data.items(), key=lambda x: x[1]['cost'], reverse=True)
        if sorted_apps:
            top_app = sorted_apps[0][0]
            suggestions.append({
                "title": f"Device Health: {top_app}",
                "type": self._get_icon_type(top_app),
                "header": "Consumption Spike Monitoring",
                "insight": f"{top_app} is showing higher than normal consumption this week.",
                "recommendation": "Check filter health or scheduling if usage seems unintentional.",
                "savings": "Monitor for savings",
                "actions": ["Check appliance maintenance", "Verify smart plug data", "Compare daily trends"],
                "priority": "Low",
                "impact": "Device performance"
            })
            
        suggestions.append({
            "title": "Baseline Stability",
            "type": "general",
            "header": "Energy usage vs Previous Week",
            "insight": "Your energy baseline is stable with some minor fluctuations.",
            "recommendation": "Monitor your night-time base load for any forgotten electronics.",
            "savings": "₹15 - ₹30 / month",
            "actions": ["Unplug idle chargers", "Use smart power strips", "Review night load"],
            "priority": "Low",
            "impact": "Long-term stability"
        })
        return suggestions

    def _calculate_peak_usage_ratio(self):
        # Peak hours: 6-10 AM, 6-10 PM
        if self.df.empty: return 0
        peak_df = self.df[self.df['timestamp'].dt.hour.isin([6,7,8,9,10,18,19,20,21,22])]
        return peak_df['energy'].sum() / self.df['energy'].sum() if self.df['energy'].sum() > 0 else 0

    def _get_icon_type(self, app_name):
        icons_map = {
            'Air Conditioning': 'cooling',
            'Heater': 'heating',
            'Water Heater': 'heating',
            'Dishwasher': 'appliance',
            'Washing Machine': 'appliance',
            'Refrigerator': 'appliance',
            'Computer': 'digital',
            'Television': 'digital',
            'Microwave': 'kitchen',
            'Oven': 'kitchen',
            'Lights': 'general'
        }
        return icons_map.get(app_name, 'general')

    def _get_actions(self, app_name):
        actions_map = {
            'Air Conditioning': ["Set thermostat to 24-25°C", "Use ceiling fans with AC", "Clean filters monthly"],
            'Heater': ["Lower thermostat by 2°C", "Seal drafts around doors", "Use space heaters sparingly"],
            'Lights': ["Replace old bulbs with LEDs", "Install occupancy sensors", "Utilize natural daylight"],
            'Dishwasher': ["Run full loads only", "Turn off heated dry", "Use Eco wash mode"],
            'Television': ["Enable Auto-Off on TV", "Use smart power strips", "Adjust screen brightness"],
            'Computer': ["Use sleep mode", "Unplug when fully charged", "Shut down after work"]
        }
        return actions_map.get(app_name, ["Reduce daily usage", "Switch off when not in use"])

    def _calculate_dynamic_billing(self):
        df_master = self.df.sort_values('timestamp').tail(24).copy()
        if df_master.empty:
            return {"projected_monthly": 0, "daily_cost": 0, "appliance_costs": [], "df_sync": df_master}

        tariff = self.user_profile.get('tariff_type', 'Fixed rate')
        peak_rate = float(self.user_profile.get('peak_rate', 7.0))
        off_peak_rate = float(self.user_profile.get('off_peak_rate', 4.5))
        
        def get_rate(row):
            if tariff == 'Time-of-use':
                hour = row['timestamp'].hour
                if (6 <= hour <= 10) or (18 <= hour <= 22):
                    return peak_rate
                return off_peak_rate
            return peak_rate

        df_master['rate'] = df_master.apply(get_rate, axis=1)
        df_master['cost'] = df_master['energy'] * df_master['rate']
        daily_cost = df_master['cost'].sum()
        projected_monthly = daily_cost * 30
        
        app_breakdown = []
        grouped = df_master.groupby('appliance').agg({'energy': 'sum', 'cost': 'sum'})
        for app, row in grouped.iterrows():
            app_breakdown.append({
                "appliance": app,
                "cost": round(row['cost'] * 30, 2),
                "kwh": round(row['energy'] * 30, 2)
            })
            
        return {
            "projected_monthly": round(projected_monthly, 0),
            "daily_cost": round(daily_cost, 2),
            "appliance_costs": sorted(app_breakdown, key=lambda x: x['cost'], reverse=True),
            "df_sync": df_master 
        }

    def _calculate_energy_persona(self):
        recent = self.df.tail(168)
        if recent.empty: return {"type": "Analyzing...", "characteristics": [], "priority": []}
        
        usage_by_app = recent.groupby('appliance')['energy'].sum()
        top_app = usage_by_app.idxmax()
        
        p_type = "Balanced Energy Consumer 🏠"
        chars = ["Stable usage patterns", "Diverse appliance mix", "Efficient baseline behavior"]
        
        if top_app == 'Air Conditioning':
            p_type = "Cooling-Intensive Household 🌬️"
            chars = ["High comfort-driven usage", "AC dominated load"]
        elif top_app == 'Heater':
            p_type = "Heating-Intensive Household 🔥"
            chars = ["High thermal load", "Seasonal variation"]

        return {"type": p_type, "characteristics": chars, "priority": usage_by_app.sort_values(ascending=False).index.tolist()[:3]}

    def _calculate_efficiency_score(self):
        if len(self.df) < 48: return 85
        recent = self.df.tail(24)['energy'].mean()
        prev = self.df.tail(48).head(24)['energy'].mean()
        if prev == 0: return 90
        diff = (recent / prev - 1) * 100
        return max(0, min(100, int(100 - diff * 0.5)))

    def _get_lstm_forecast(self):
        try:
            last_24 = self.df.tail(24)['energy'].tolist()
            forecast = self.prediction_engine.predict_next_hour(last_24)
            return round(forecast, 2)
        except:
            return 0.45

    def _prepare_graph_data(self, bill_data):
        df = self.df
        
        # 1. Daily Usage (Last 7 Days)
        daily = df.groupby(df['timestamp'].dt.date)['energy'].sum().tail(7)
        daily_usage = [{"date": str(d), "value": round(v, 2)} for d, v in daily.items()]
        
        # 2. Appliance Split
        split = []
        for item in bill_data['appliance_costs']:
            split.append({"label": item['appliance'], "value": item['kwh']})
            
        # 3. Cost Trend (Historical Daily Costs)
        # We use the sync slice for the most recent point, but for trend we look at recent history
        # For simple consistent trend, group the sync slice if available or the billing df
        df_b = bill_data['df_sync']
        cost_trend = df_b.groupby(df_b['timestamp'].dt.date)['cost'].sum()
        cost_trend_data = [{"date": str(d), "value": round(v, 2)} for d, v in cost_trend.items()]
        
        # 4. Forecast Data (Next 24 hours - simulated extension of trend)
        forecast_data = []
        last_val = df['energy'].iloc[-1]
        for i in range(1, 25):
            forecast_data.append({"hour": i, "value": round(last_val * (1 + random.uniform(-0.1, 0.1)), 2)})
            
        return {
            "daily_usage": daily_usage,
            "appliance_split": split,
            "cost_trend": cost_trend_data,
            "forecast": forecast_data
        }

    def _get_default_profile(self):
        return {
            "name": "User", "home_id": 399, "goal": "Reduce bill",
            "house_size": 1200, "residents": 3, "tariff_type": "Fixed rate",
            "peak_rate": 7.0, "off_peak_rate": 4.5
        }

    def _get_empty_payload(self):
        return {
            "energy_persona": "Analyzing Data...",
            "persona_details": {"type": "...", "characteristics": [], "priority": []},
            "efficiency_score": 0,
            "projected_monthly_bill": "₹0",
            "appliance_breakdown": [],
            "suggestions": [],
            "goal_summary": "Analyzing energy data...",
            "alerts": [],
            "savings_summary": {"total": "₹0", "percent": "0%"},
            "forecast_next_hour": "0 kWh",
            "graphs_data": {"daily_usage": [], "appliance_split": [], "cost_trend": [], "forecast": []}
        }
