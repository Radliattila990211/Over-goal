import streamlit as st
import requests
from datetime import datetime

API_TOKEN = "YOUR_API_KEY"
BASE_URL = f"https://api.sportmonks.com/v3/football/livescores?api_token={API_TOKEN}&include=participants;statistics;scores"

def fetch_live_matches():
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        data = response.json()
        return data.get("data", []), None
    except Exception as e:
        return [], f"Hiba az API elérésében: {e}"

def is_match_live(match):
    state_id = match.get('state_id', 0)
    if state_id in (2, 3):
        return True
    return False

def main():
    st.title("Élő foci meccsek és stratégiák")

    matches, error = fetch_live_matches()
    if error:
        st.error(error)
        return

    if not matches:
        st.info("⚠️ Nincs jelenleg meccs az API szerint.")
        return

    live_matches = [m for m in matches if is_match_live(m)]

    if not live_matches:
        st.info("⚠️ Jelenleg nincs élő meccs az API szerint.")
        return

    st.header("Élőben zajló meccsek")
    for m in live_matches:
        st.write(f"{m['name']} — Állapot: {m.get('state_id')} — Kezdés: {m['starting_at']}")

    # Itt jöhet a stratégiák megjelenítése (ha akarod)

if __name__ == "__main__":
    main()
