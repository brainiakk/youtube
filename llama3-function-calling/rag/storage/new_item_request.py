import requests
url = "http://localhost:5000/items"
headers = {"Content-Type": "application/json"}
data = {"name": "New Item", "description": "This is a new item"}
response = requests.post(url, headers=headers, json=data)