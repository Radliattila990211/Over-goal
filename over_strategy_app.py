import requests
API_TOKEN = "iV9xxHhZkgZQqudhrzq2r697fd21b9VcR3z50gSFpXV9K4Yimvj4HWBFf3Mn"
url = f"https://api.sportmonks.com/v3/football/livescores/inplay?api_token={API_TOKEN}"
response = requests.get(url)
data = response.json()
print(data['data'][:2])  # az első 2 meccs JSON adata
