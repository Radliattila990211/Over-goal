import streamlit as st
import requests
from datetime import datetime

# --- API kulcs és alap URL ---
API_KEY = "iV9xxHhZkgZQqudhrzq2r697fd21b9VcR3z50gSFpXV9K4Yimvj4HWBFf3Mn"
BASE_URL = "https://api.sportmonks.com/v3/football"

# --- Élő meccsek lekérése ---
def get_live_matches():
    url = f"{BASE_URL}/livescores/inplay?include=events,statistics,teams&api_token={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Hiba az API elérésében: {response.status_code}")
        return []
    data = response.json()
    return data.get("data", [])

# --- Feltételek: Első félidő + 70. perc után ---
def analyze_match(match):
    try:
        home_team = match['home_team']['name']
        away_team = match['away_team']['name']
        minute = match.get("time", {}).get("minute", 0)
        status = match['time']['status']
        home_score = int(match["scores"]["home_score"])
        away_score = int(match["scores"]["away_score"])
    except:
        return None  # ha hiányzik adat

    result = {
        "match": f"{home_team} - {away_team}",
        "minute": minute,
        "score": f"{home_score} - {away_score}",
        "status": status,
        "strategy1": False,
        "strategy2": False,
    }

    total_goals = home_score + away_score

    # Stratégia 1: Első félidő több mint 0.5 gól (ha 0 gól van 45. percig)
    if minute <= 45 and total_goals == 0:
        result["strategy1"] = True

    # Stratégia 2: 70. perc után, kevés gól
    if minute >= 70 and total_goals <= 1:
        result["strategy2"] = True

    return result

# --- Streamlit UI ---
st.set_page_config(page_title="⚽ Élő Foci Stratégiák", layout="wide")
st.title("⚽ Élő Foci Sportfogadási Stratégia - Sportmonks API")

matches = get_live_matches()

if not matches:
    st.warning("❗ Jelenleg nincs élő meccs az API szerint.")
else:
    for match in matches:
        analysis = analyze_match(match)
        if not analysis:
            continue

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(analysis["match"])
            st.markdown(
                f"🕒 Perc: `{analysis['minute']}` | Állás: `{analysis['score']}` | Státusz: `{analysis['status']}`"
            )

        with col2:
            if analysis["strategy1"]:
                st.success("✅ **Stratégia 1: FH Over 0.5 gól ajánlott!**")
            if analysis["strategy2"]:
                st.info("⚠️ **Stratégia 2: Gólvárás a 70. perc után!**")

st.markdown("---")
st.caption("Adatok: Sportmonks Football API | App by Radli Attila")
