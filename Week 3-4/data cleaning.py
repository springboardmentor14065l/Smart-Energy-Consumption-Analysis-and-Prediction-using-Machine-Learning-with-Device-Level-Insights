import pandas as pd
import numpy as np

data = pd.DataFrame({
    "timestamp": [
        "2026-01-02 08:00", "2026-01-06 08:00",
        "2026-01-02 09:00", "2026-01-07 09:00",
        "2026-01-01 10:00", "2026-01-03 10:00",
        "2026-01-04 11:00", "2026-01-01 11:00"
    ],
    "device": [
        "AC", "Fridge",
        "AC", "Fridge",
        "TV", "Fan",
        "Washing Machine", "Light"
    ],
    "energy": [1.5, 0.3, 1.8, 0.4, 0.6, 0.2, 1.2, 0.1]
})


data["timestamp"] = pd.to_datetime(data["timestamp"])
data.dropna(inplace=True)
data.drop_duplicates(inplace=True)
data["hour"] = data["timestamp"].dt.hour

print("Cleaned Dataset:")
print(data)
