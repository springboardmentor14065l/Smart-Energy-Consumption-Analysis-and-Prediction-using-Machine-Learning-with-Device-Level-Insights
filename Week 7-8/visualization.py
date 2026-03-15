import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os

class Visualizer:
    def __init__(self, data_path, output_dir):
        self.data_path = data_path
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.df = None
        self._load_data()

    def _load_data(self):
        if os.path.exists(self.data_path):
            self.df = pd.read_csv(self.data_path)
            self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'])
            self.df.rename(columns={'Energy Consumption (kWh)': 'energy'}, inplace=True)
        else:
            print(f"Data file not found at {self.data_path}")

    def generate_all_charts(self):
        if self.df is None:
            return
        
        self.generate_trends()
        self.generate_device_usage()

    def generate_trends(self):
        # Set style
        plt.style.use('dark_background')
        
        # 1. Hourly Trend (Last 24 hours of data)
        plt.figure(figsize=(15, 8), dpi=100)
        recent_24 = self.df.sort_values('Timestamp').tail(24)
        plt.plot(recent_24['Timestamp'], recent_24['energy'], marker='o', linestyle='-', color='#00d7ff', linewidth=2)
        plt.title('Hourly Energy Consumption Trend (Last 24 Hours)', color='white', fontsize=16)
        plt.xlabel('Time', color='white', fontsize=12)
        plt.ylabel('kWh', color='white', fontsize=12)
        plt.grid(True, alpha=0.2)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'hourly_trend.png'))
        plt.close()

        # 2. Daily Trend (Group by Date)
        plt.figure(figsize=(15, 8), dpi=100)
        daily = self.df.groupby(self.df['Timestamp'].dt.date)['energy'].sum().tail(7)
        daily.plot(kind='bar', color='#00af00', width=0.7)
        plt.title('Daily Energy Consumption (Last 7 Days)', color='white', fontsize=16)
        plt.xlabel('Date', color='white', fontsize=12)
        plt.ylabel('Total kWh', color='white', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'daily_trend.png'))
        plt.close()

    def generate_device_usage(self):
        plt.style.use('dark_background')
        
        # Device-wise usage pie chart
        device_usage = self.df.groupby('Appliance Type')['energy'].sum()
        
        plt.figure(figsize=(8, 8))
        colors = plt.cm.viridis(np.linspace(0, 1, len(device_usage)))
        plt.pie(device_usage, labels=device_usage.index, autopct='%1.1f%%', colors=colors, startangle=140)
        plt.title('Energy Distribution by Device', color='white')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'device_usage.png'))
        plt.close()

if __name__ == "__main__":
    visualizer = Visualizer(
        data_path=r"c:\001 PROJECTS\Infosys Internship\Week 1-2\Ready For Feature Eng dataset\cleaned_energy_consumption_data.csv",
        output_dir=r"c:\001 PROJECTS\Infosys Internship\Week 7-8\static\images"
    )
    visualizer.generate_all_charts()
    print("Charts generated successfully.")
