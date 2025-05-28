import streamlit as st
import requests

st.set_page_config(page_title="Élő Foci Stratégiák Debug", layout="wide")

API_KEY = st.secrets["API_KEY"]

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

@st.cache_data(ttl=30)
def get_live_fixtures():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all"
    response = requests.get(url, headers=headers)
    st.write("API státusz:", response.status_code)
    try:
        data = response.json()
        st.write("API raw válasz:", data)
        fixtures = data.get("response", [])
        return fixtures
    except Exception as e:
        st.error(f"Hiba az API válasz feldolgozásánál: {e}")
        return []

st.title("⚽ Élő Foci Stratégiák - Debug verzió")

fixtures = get_live_fixtures()

if not fixtures:
    st.warning("Nincsenek élő meccsek vagy probléma az API hívással.")
else:
    st.success(f"Élő meccsek száma: {len(fixtures)}")
    for match in fixtures:
        league = match.get("league", {}).get("name", "Ismeretlen liga")
        home = match.get("teams", {}).get("home", {}).get("name", "Hazai")
        away = match.get("teams", {}).get("away", {}).get("name", "Vendég")
        score_home = match.get("goals", {}).get("home", 0)
        score_away = match.get("goals", {}).get("away", 0)
        elapsed = match.get("fixture", {}).get("status", {}).get("elapsed", 0)
        
        st.write(f"**{league}** — {home} vs {away} — Eredmény: {score_home} : {score_away} — {elapsed}'")
