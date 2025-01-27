import re
from datetime import datetime

import pandas as pd
import requests

from .Dictionaries import team_index_current

games_header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/57.0.2987.133 Safari/537.36',
    'Dnt': '1',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en',
    'origin': 'http://stats.nba.com',
    'Referer': 'https://github.com'
}

data_headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.nba.com/',
    'Connection': 'keep-alive'
}


def get_json_data(url):
    raw_data = requests.get(url, headers=data_headers)
    try:
        json = raw_data.json()
    except Exception as e:
        print(e)
        return {}
    return json.get('resultSets')


def get_todays_games_json(url):
    raw_data = requests.get(url, headers=games_header)
    json = raw_data.json()
    return json.get('gs').get('g')


def to_data_frame(data):
    try:
        data_list = data[0]
    except Exception as e:
        print(e)
        return pd.DataFrame(data={})
    return pd.DataFrame(data=data_list.get('rowSet'), columns=data_list.get('headers'))


def create_todays_games(input_list):
    games = []
    for game in input_list:
        home = game.get('h')
        away = game.get('v')
        home_team = home.get('tc') + ' ' + home.get('tn')
        away_team = away.get('tc') + ' ' + away.get('tn')
        games.append([home_team, away_team])
    return games


def create_todays_games_from_odds(input_dict):
    games = []
    for game in input_dict.keys():
        home_team, away_team = game.split(":")
        if home_team not in team_index_current or away_team not in team_index_current:
            continue
        games.append([home_team, away_team])
    return games


def get_date(date_string):
    year1, month, day = re.search(r'(\d+)-\d+-(\d\d)(\d\d)', date_string).groups()
    year = year1 if int(month) > 8 else int(year1) + 1
    return datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d')





def build_darko_sums(daily_csv, today_matches):
    """
    Reads daily_projections.csv, sums the PTS column by team,
    then returns a dict keyed by (home, away) => (darko_home_pts, darko_away_pts).
    """
    df = pd.read_csv(daily_csv)
    # find PTS column
    pts_col = None
    for c in df.columns:
        if "PTS" in c.upper():
            pts_col = c
            break
    if not pts_col:
        raise ValueError("Could not find PTS column in daily CSV.")
    df[pts_col] = pd.to_numeric(df[pts_col], errors="coerce")

    sums_by_team = df.groupby("SearchTeam")[pts_col].sum().to_dict()

    out = {}
    for (home, away) in today_matches:
        home_pts = sums_by_team.get(home, 0.0)
        away_pts = sums_by_team.get(away, 0.0)
        out[(home, away)] = (home_pts, away_pts)
    return out

def load_skill_data(skill_csv):
    df_skill = pd.read_csv(skill_csv)
    if "DPM" in df_skill.columns:
        df_skill["DPM"] = pd.to_numeric(df_skill["DPM"], errors="coerce")
    return df_skill

def load_lineup_data(lineup_csv):
    df_lineup = pd.read_csv(lineup_csv)
    if "Net" in df_lineup.columns:
        df_lineup["Net"] = pd.to_numeric(df_lineup["Net"], errors="coerce")
    return df_lineup