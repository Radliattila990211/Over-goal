import streamlit as st
import requests
from datetime import datetime

# --- API kulcs és alap URL ---
API_KEY = "X7PIOp7qahwTboQi9AS8IZFXSIeSdjq0vR1Gpo8YsLk7hFr4NyceZvV74i70"
BASE_URL = "https://api.sportmonks.com/v3/football"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

# --- Élő meccsek lekérése ---
def get_live_matches():
    url = f"{BASE_URL}/livescores?include=events,statistics,teams"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        st.error(f"Hiba az API elérésében: {response.status_code}")
        return []
    data = response.json()
    return data.get("data", [])

# --- Feltételek: Első félidő + 70. perc után ---
def analyze_match(match):
    result = {
        "match": f"{match['home_team']['name']} - {match['away_team']['name']}",
        "minute": match.get("time", {}).get("minute", 0),
        "score": f"{match['scores']['home_score']} - {match['scores']['away_score']}",
        "status": match['time']['status'],
        "strategy1": False,
        "strategy2": False,
    }

    minute = int(match.get("time", {}).get("minute", 0))
    home_goals = int(match["scores"]["home_score"])
    away_goals = int(match["scores"]["away_score"])
    total_goals = home_goals + away_goals

    # Stratégia 1: Első félidő több mint 0.5 gól
    if minute <= 45 and total_goals == 0:
        result["strategy1"] = True

    # Stratégia 2: 70. perc után, döntetlen, nincs gól az utóbbi időben
    if minute >= 70 and total_goals <= 1:
        result["strategy2"] = True

    return result

# --- Streamlit UI ---
st.set_page_config(page_title="Élő Foci Stratégia", layout="wide")
st.title("⚽ Élő Foci Sportfogadási Stratégia - Sportmonks API")

matches = get_live_matches()

if not matches:
    st.warning("Jelenleg nincs elérhető élő meccs az API szerint.")
else:
    for match in matches:
        analysis = analyze_match(match)
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(analysis["match"])
            st.markdown(f"🕒 Perc: `{analysis['minute']}` | Állás: `{analysis['score']}` | Státusz: `{analysis['status']}`")

        with col2:
            if analysis["strategy1"]:
                st.success("✅ **Stratégia 1 - FH Over 0.5 ajánlott!**")
            if analysis["strategy2"]:
                st.info("⚠️ **Stratégia 2 - 70. perc utáni gólvárás!**")

st.markdown("---")
st.caption("Adatok: Sportmonks Football API | Készítette: Radli Attila")
