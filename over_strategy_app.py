import streamlit as st
import requests

# API beállítások
API_TOKEN = "iV9xxHhZkgZQqudhrzq2r697fd21b9VcR3z50gSFpXV9K4Yimvj4HWBFf3Mn"
BASE_URL = "https://api.sportmonks.com/v3/football"
HEADERS = {
    "accept": "application/json"
}

def get_live_matches():
    url = f"{BASE_URL}/livescores/inplay?api_token={API_TOKEN}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    else:
        st.error(f"Hiba az API elérésében: {response.status_code}")
        return []

def parse_match(match):
    try:
        home = match['participants']['home']['name']
        away = match['participants']['away']['name']

        home_score = match['scores']['home_score']
        away_score = match['scores']['away_score']
        score = f"{home_score} - {away_score}"

        minute = match.get('time', {}).get('minute', '?')
        status = match.get('time', {}).get('status', 'unknown')
        period = match.get('time', {}).get('period', '')

        # Statisztikákból labdabirtoklás (ha elérhető)
        possession_home = "?"
        possession_away = "?"
        stats = match.get('statistics', {}).get('data', {})
        if stats and 'possession' in stats:
            possession_home = stats['possession'].get('home', "?")
            possession_away = stats['possession'].get('away', "?")

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
    try:
        minute = int(match_data["minute"]) if match_data["minute"] != '?' else 0
        goals = sum(int(g) for g in match_data["score"].split(" - "))

        # Stratégiák:
        # 1) Első félidő több mint 0.5 gólra még nincs gól 10-45. perc között
        strat_over_0_5_ht = False
        if match_data["period"] == "1st" and 10 <= minute <= 45 and goals == 0:
            strat_over_0_5_ht = True

        # 2) Teljes meccsen több mint 1.5 gólra, ha még nincs gól 20-70. perc között
        strat_over_1_5_ft = False
        if 20 <= minute <= 70 and goals == 0:
            strat_over_1_5_ft = True

        return strat_over_0_5_ht, strat_over_1_5_ft
    except Exception as e:
        st.warning(f"Hiba a stratégia ellenőrzésénél: {e}")
        return False, False

# Streamlit app kezdete
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

        strat_0_5_ht, strat_1_5_ft = check_strategies(parsed)

        with st.expander(f"🔹 {parsed['home']} vs {parsed['away']} | ⏱ {parsed['minute']}' - {parsed['score']}"):
            st.markdown(f"**Állás:** {parsed['score']}  \n"
                        f"**Perc:** {parsed['minute']} ({parsed['period']})  \n"
                        f"**Labdabirtoklás:** {parsed['possession_home']}% - {parsed['possession_away']}%")

            if strat_0_5_ht:
                st.success("✅ **Jelzés: Első félidő több mint 0,5 gól várható**")

            if strat_1_5_ft:
                st.info("📈 **Jelzés: Teljes meccsen több mint 1,5 gól várható**")
