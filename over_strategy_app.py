import streamlit as st
import requests
import pandas as pd

# API-Football kulcs
API_KEY = "fe42fb2bd6d9cbd944bd3533bb53b82f"
HEADERS = {"x-apisports-key": API_KEY}
BASE_URL = "https://v3.football.api-sports.io"

# Élő meccsek lekérése
def get_live_matches():
    url = f"{BASE_URL}/fixtures?live=all"
    r = requests.get(url, headers=HEADERS)
    return r.json().get('response', [])

# Statisztikák lekérése
def get_stats(fixture_id):
    url = f"{BASE_URL}/fixtures/statistics?fixture={fixture_id}"
    r = requests.get(url, headers=HEADERS)
    return r.json().get('response', [])

# Meccs info kinyerése
def extract_match_info(match):
    time = match['fixture']['status']['elapsed']
    home = match['teams']['home']['name']
    away = match['teams']['away']['name']
    score_home = match['goals']['home']
    score_away = match['goals']['away']
    return {
        'time': time, 'home': home, 'away': away,
        'score': f"{score_home}-{score_away}",
        'score_home': score_home, 'score_away': score_away,
        'id': match['fixture']['id']
    }

# Stat feldolgozás
def parse_statistics(stats):
    res = {'shots_total': 0, 'shots_on_goal': 0, 'possession_home': 0, 'possession_away': 0}
    for team_stats in stats:
        for stat in team_stats['statistics']:
            if stat['type'] == 'Total Shots':
                res['shots_total'] += stat['value'] or 0
            elif stat['type'] == 'Shots on Goal':
                res['shots_on_goal'] += stat['value'] or 0
            elif stat['type'] == 'Ball Possession':
                val = int(stat['value'].replace('%', '')) if stat['value'] else 0
                if team_stats['team']['id'] == stats[0]['team']['id']:
                    res['possession_home'] = val
                else:
                    res['possession_away'] = val
    return res

# Streamlit UI
st.set_page_config(page_title="Élő Sportfogadás", layout="wide")
st.title("⚽ Élő Sportfogadási Stratégia – 5.000 Ft bankroll")
st.caption("Stratégiák: 70. perc utáni gól + első félidő 0.5 gól felett")

matches = get_live_matches()

# 📺 Élő meccsek kilistázása
st.subheader("📺 Élőben futó meccsek")
if matches:
    live_list = []
    for match in matches:
        info = extract_match_info(match)
        live_list.append({
            'Meccs': f"{info['home']} - {info['away']}",
            'Állás': info['score'],
            'Perc': info['time']
        })
    st.dataframe(pd.DataFrame(live_list))
else:
    st.info("Jelenleg nincs élő meccs az API-n.")

# Elemzett meccsek
late_goals = []
first_half_goals = []

for match in matches:
    info = extract_match_info(match)
    stats = get_stats(info['id'])
    parsed = parse_statistics(stats)

    # 70. perc utáni stratégia
    if info['time'] and info['time'] >= 70 and info['score'] in ['0-0', '1-0', '1-1', '0-1']:
        if parsed['shots_on_goal'] >= 2 and (parsed['possession_home'] > 60 or parsed['possession_away'] > 60):
            late_goals.append({
                'Meccs': f"{info['home']} - {info['away']}",
                'Állás': info['score'],
                'Perc': info['time'],
                'Kapuralövések': parsed['shots_on_goal'],
                'Labdabirtoklás': f"{parsed['possession_home']}% - {parsed['possession_
