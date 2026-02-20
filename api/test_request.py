import requests

url = "http://127.0.0.1:5000/predict"

data = {
    "appliance": "Fridge",
    "last_values": [0.1]*24
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Raw Response:", response.text)
