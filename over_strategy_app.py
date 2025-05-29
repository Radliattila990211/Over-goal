import streamlit as st
import requests
from datetime import datetime

# Sportmonks API beállítások
API_TOKEN = "iV9xxHhZkgZQqudhrzq2r697fd21b9VcR3z50gSFpXV9K4Yimvj4HWBFf3Mn"
BASE_URL = "https://api.sportmonks.com/v3/football"

headers = {
    "accept": "application/json"
}

def get_live_matches():
    url = f"{BASE_URL}/livescores/inplay?api_token={API_TOKEN}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    else:
        st.error(f"Hiba az API elérésében: {response.status_code}")
        return []

def parse_match(match):
    try:
        home = match['home_team']['name']
        away = match['away_team']['name']
        score = f"{match['scores']['home_score']} - {match['scores']['away_score']}"
        minute = match.get('time', {}).get('minute', '?')
        status = match.get('time', {}).get('status', 'unknown')
        period = match.get('time', {}).get('period', '')
        stats = match.get('stats', {})

        possession_home = stats.get('possession', {}).get('data', [{}])[0].get('value', '?')
        possession_away = stats.get('possession', {}).get('data', [{}])[1].get('value', '?')

        return {
            "home": home,
            "away": away,
            "score": score,
            "minute": minute,
            "status": status,
            "period": period,
            "possession_home": possession_home,
            "possession_away": possession_away
        }
    except Exception as e:
        st.warning(f"Nem sikerült feldolgozni egy meccset: {e}")
        return None

def check_strategies(match_data):
    minute = int(match_data["minute"]) if match_data["minute"] != '?' else 0
    goals = sum(int(g) for g in match_data["score"].split(" - "))

    strat_1 = False
    strat_2 = False

    if match_data["period"] == "1st" and 10 <= minute <= 45 and goals == 0:
        strat_1 = True

    if goals == 0 and 20 <= minute <= 70:
        strat_2 = True

    return strat_1, strat_2

# Streamlit alkalmazás
st.set_page_config(page_title="⚽ Élő Sportfogadási Jelzések", layout="wide")
st.title("📊 Élő Sportfogadási Stratégia Jelzések")
st.markdown("🔄 Az adatok valós időben frissülnek az API alapján.")

matches = get_live_matches()

if not matches:
    st.warning("❗ Jelenleg nincs élő meccs az API szerint.")
else:
    for match in matches:
        parsed = parse_match(match)
        if not parsed:
            continue

        strat_1, strat_2 = check_strategies(parsed)

        with st.expander(f"🔹 {parsed['home']} vs {parsed['away']} | ⏱ {parsed['minute']}' - {parsed['score']}"):
            st.markdown(f"**Állás:** {parsed['score']}  \n"
                        f"**Perc:** {parsed['minute']} ({parsed['period']})  \n"
                        f"**Labdabirtoklás:** {parsed['possession_home']}% - {parsed['possession_away']}%")

            if strat_1:
                st.success("✅ **Jelzés: Over 0.5 gól az első félidőben**")

            if strat_2:
                st.info("📈 **Jelzés: Over 1.5 gól az egész meccsen**")
