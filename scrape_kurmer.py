import requests
import pandas as pd

json_url = "https://api.buku.cloudapp.web.id/api/catalogue/getPenggerakTextBooks?limit=2000&type_pdf&order_by=updated_at"

response = requests.get(json_url)
response.raise_for_status()

data = response.json()

if isinstance(data, dict):
    for value in data.values():
        if isinstance(value, list):
            data = value
            break

df = pd.DataFrame(data)
df.to_csv('output_kurmer.csv', index=False)

print("CSV saved as output_kurmer.csv")