import sqlite3
import os
import pandas as pd

class DatabaseManager:
    def __init__(self, db_path='database.db'):
        self.db_path = db_path
        self.init_db()
        self.migrate_schema()

    def get_connection(self):
        # Use a timeout of 30 seconds to prevent "database is locked" errors
        return sqlite3.connect(self.db_path, timeout=30.0)

    def migrate_schema(self):
        """Self-healing migration to add missing columns."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check user_preferences
            cursor.execute("PRAGMA table_info(user_preferences)")
            cols = [row[1] for row in cursor.fetchall()]
            if 'home_id' not in cols:
                print("Migrating: Adding home_id to user_preferences")
                cursor.execute("ALTER TABLE user_preferences ADD COLUMN home_id INTEGER")
            
            # Check consumption_data (already has it in current init_db, but good for safety)
            cursor.execute("PRAGMA table_info(consumption_data)")
            cols = [row[1] for row in cursor.fetchall()]
            if 'home_id' not in cols:
                print("Migrating: Adding home_id to consumption_data")
                cursor.execute("ALTER TABLE consumption_data ADD COLUMN home_id INTEGER")
            conn.commit()

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    city TEXT
                )
            ''')
            
            # Create user_preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER PRIMARY KEY,
                    home_id INTEGER,
                    house_size INTEGER,
                    residents INTEGER,
                    ac_type TEXT,
                    solar_panels BOOLEAN,
                    lifestyle_pattern TEXT,
                    goal TEXT,
                    tariff_type TEXT,
                    peak_rate REAL,
                    off_peak_rate REAL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create consumption_data table (Now with home_id)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consumption_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    home_id INTEGER,
                    timestamp DATETIME,
                    kwh REAL,
                    appliance TEXT,
                    temperature REAL
                )
            ''')
            conn.commit()

    def get_random_home_id(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT home_id FROM consumption_data LIMIT 50")
            ids = [row[0] for row in cursor.fetchall()]
        
        import random
        return random.choice(ids) if ids else 1

    def save_user_profile(self, profile_data):
        # Pick specific home_id or assign random one
        home_id = profile_data.get('home_id') or self.get_random_home_id()
        user_id = 1 # Simplified for demo

        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Insert or update user
            cursor.execute('''
                INSERT OR REPLACE INTO users (id, name, city)
                VALUES (?, ?, ?)
            ''', (user_id, profile_data.get('name', 'User'), profile_data.get('city')))
            
            # Insert or update preferences
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (
                    user_id, home_id, house_size, residents, ac_type, solar_panels, 
                    lifestyle_pattern, goal, tariff_type, peak_rate, off_peak_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                home_id,
                profile_data.get('house_size'),
                profile_data.get('residents'),
                profile_data.get('ac_type'),
                profile_data.get('solar_panels'),
                profile_data.get('lifestyle_pattern'),
                profile_data.get('goal'),
                profile_data.get('tariff_type'),
                profile_data.get('peak_rate', 7.0),
                profile_data.get('off_peak_rate', 4.5)
            ))
            conn.commit()
        return user_id

    def get_user_profile(self, user_id=1):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM users u
                JOIN user_preferences p ON u.id = p.user_id
                WHERE u.id = ?
            ''', (user_id,))
            row = cursor.fetchone()
        
        return dict(row) if row else None

    def import_csv_to_db(self, csv_path):
        if not os.path.exists(csv_path):
            return
        
        df = pd.read_csv(csv_path)
        df_db = pd.DataFrame({
            'home_id': df['Home ID'],
            'timestamp': pd.to_datetime(df['Timestamp']),
            'kwh': df['Energy Consumption (kWh)'],
            'appliance': df['Appliance Type'],
            'temperature': df['Outdoor Temperature']
        })
        
        with self.get_connection() as conn:
            df_db.to_sql('consumption_data', conn, if_exists='replace', index=False)

if __name__ == "__main__":
    db = DatabaseManager()
    # Test path
    csv_path = r"c:\001 PROJECTS\Infosys Internship\Week 1-2\Ready For Feature Eng dataset\cleaned_energy_consumption_data.csv"
    db.import_csv_to_db(csv_path)
