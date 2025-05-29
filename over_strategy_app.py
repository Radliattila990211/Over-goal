import streamlit as st
import requests

API_TOKEN = "iV9xxHhZkgZQqudhrzq2r697fd21b9VcR3z50gSFpXV9K4Yimvj4HWBFf3Mn"
BASE_URL = "https://api.sportmonks.com/v3/football"

def get_live_matches():
    url = f"{BASE_URL}/livescores?api_token={API_TOKEN}&include=participants;statistics;scores;time"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            st.error(f"Hiba az API elérésében: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Hiba történt: {e}")
        return []

def parse_match_data(match):
    try:
        home_team = match['participants'][0]['name']
        away_team = match['participants'][1]['name']
        score = match['scores']['ft_score']
        minute = int(match['time']['minute'])

        stats = {s['type']: s for s in match.get('statistics', [])}

        total_shots = int(stats.get('shots_total', {}).get('home', 0)) + int(stats.get('shots_total', {}).get('away', 0))
        shots_on_target = int(stats.get('shots_on_target', {}).get('home', 0)) + int(stats.get('shots_on_target', {}).get('away', 0))
        possession_home = int(stats.get('ball_possession', {}).get('home', 0))
        possession_away = int(stats.get('ball_possession', {}).get('away', 0))

        return {
            'home': home_team,
            'away': away_team,
            'score': score,
            'minute': minute,
            'shots_total': total_shots,
            'shots_on_target': shots_on_target,
            'possession': f"{possession_home}% - {possession_away}%"
        }
    except Exception as e:
        st.warning(f"Nem sikerült feldolgozni egy meccset: {e}")
        return None

def goal_after_70_strategy(parsed):
    if parsed and 70 <= parsed['minute'] <= 90:
        if parsed['score'] in ['0-0', '1-0', '0-1', '1-1']:
            if parsed['shots_total'] >= 15 and parsed['shots_on_target'] >= 5:
                return True
    return False

def first_half_goal_strategy(parsed):
    if parsed and 1 <= parsed['minute'] <= 45:
        if parsed['shots_total'] >= 5 and parsed['shots_on_target'] >= 2:
            return True
    return False

# Streamlit UI
st.title("📊 Élő Sportfogadási Stratégia Jelzések")

matches = get_live_matches()

if not matches:
    st.info("🔄 Jelenleg nincs élő meccs vagy hiba történt az API elérésében.")
else:
    strategy_70 = []
    strategy_first_half = []

    for match in matches:
        parsed = parse_match_data(match)
        if goal_after_70_strategy(parsed):
            strategy_70.append(parsed)
        if first_half_goal_strategy(parsed):
            strategy_first_half.append(parsed)

    st.subheader("1️⃣ 70. perc utáni gól stratégia")
    if strategy_70:
        for match in strategy_70:
            st.markdown(f"**{match['home']} vs {match['away']}** - {match['score']} ({match['minute']}. perc)")
            st.text(f"Kapuralövések: {match['shots_on_target']}, Összes lövés: {match['shots_total']}, Labdabirtoklás: {match['possession']}")
            st.markdown("---")
    else:
        st.info("Nincs olyan meccs, amely megfelel a 70. perc utáni gól stratégiának.")

    st.subheader("2️⃣ Első félidő +0.5 gól stratégia")
    if strategy_first_half:
        for match in strategy_first_half:
            st.markdown(f"**{match['home']} vs {match['away']}** - {match['score']} ({match['minute']}. perc)")
            st.text(f"Kapuralövések: {match['shots_on_target']}, Összes lövés: {match['shots_total']}, Labdabirtoklás: {match['possession']}")
            st.markdown("---")
    else:
        st.info("Nincs olyan meccs, amely megfelel az első félidős gól stratégiának.")
