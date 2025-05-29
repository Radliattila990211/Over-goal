import streamlit as st
import requests

API_TOKEN = "iV9xxHhZkgZQqudhrzq2r697fd21b9VcR3z50gSFpXV9K4Yimvj4HWBFf3Mn"
BASE_URL = "https://api.sportmonks.com/v3/football"

def get_live_matches():
    url = f"{BASE_URL}/livescores/inplay?api_token={API_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        st.write("API válasz (élő meccsek):", data)
        return data.get('data', [])
    else:
        st.error(f"Hiba az API elérésében: {response.status_code}")
        return []

matches = get_live_matches()
st.write(f"Élő meccsek száma: {len(matches)}")
