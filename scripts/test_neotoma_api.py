import requests
import pandas as pd

headers = {
    "Accept": "application/json"
}

params = {
    "database": "European Pollen Database", # change later
    "limit": 100
}

response = requests.get(
    "https://api.neotomadb.org/v2.0/data/sites",
    headers=headers,
    params=params,
    timeout=30
)

print(response.status_code)
print(response.headers.get("Content-Type"))

response.raise_for_status()

data = response.json()
df = pd.DataFrame(data)
print(df.head())
print(len(df))