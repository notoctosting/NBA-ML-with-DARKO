# darko_metrics.py

import pandas as pd
import numpy as np

def load_skill_data(skill_csv):
    df_skill = pd.read_csv(skill_csv)
    # Ensure numeric columns
    for col in ["DPM", "O-DPM", "D-DPM"]:
        if col in df_skill.columns:
            df_skill[col] = pd.to_numeric(df_skill[col], errors="coerce")
    return df_skill

def load_lineup_data(lineup_csv):
    df_lineup = pd.read_csv(lineup_csv)
    if "Net" in df_lineup.columns:
        df_lineup["Net"] = pd.to_numeric(df_lineup["Net"], errors="coerce")
    return df_lineup

def load_daily_data(daily_csv):
    df_daily = pd.read_csv(daily_csv)
    # Identify "PTS" or "MIN" columns if they exist
    # For Weighted DPM, we might also want minutes. 
    # But let's do a simpler approach: we'll use skill data's DPM with top 8 players
    return df_daily

def compute_weighted_dpm(df_skill, team_name, top_n=8):
    """
    Summation of top 'n' DPM players for this team, 
    or if you want weighting by daily minutes, you'd merge with daily data.
    For now, let's do top 8 DPM (excluding negative? or not).
    """
    team_df = df_skill[df_skill["Team"]==team_name].copy()
    # Sort by DPM desc, keep top n
    top_players = team_df.sort_values("DPM", ascending=False).head(top_n)
    return top_players["DPM"].sum()

def compute_off_def_splits(df_skill, team_name, top_n=8):
    """
    Summation of top 'n' O-DPM and D-DPM.
    Could be partial if some columns not present.
    """
    team_df = df_skill[df_skill["Team"]==team_name].copy()
    team_df = team_df.sort_values("DPM", ascending=False).head(top_n)
    sum_o = team_df["O-DPM"].sum() if "O-DPM" in team_df.columns else 0
    sum_d = team_df["D-DPM"].sum() if "D-DPM" in team_df.columns else 0
    return sum_o, sum_d

def compute_momentum_score(df_skill, team_name):
    """
    Example approach: compare each player's current DPM to their 'season avg' if available.
    If skill CSV doesn't have a time-series, we might rely on a 'DPM Improvement' column.
    E.g. if there's a column "DPM Improvement" in the skill data 
    or we do "DPM Improvement" = "DPM Improvement" * something
    We'll just check if there's "DPM Improvement" col:
    """
    team_df = df_skill[df_skill["Team"]==team_name].copy()
    if "DPM Improvement" in team_df.columns:
        # sum it
        return team_df["DPM Improvement"].sum()
    else:
        # fallback, 0
        return 0

def compute_lineup_overlap_strength(df_lineup, team_name, top_n=1):
    """
    Suppose we pick the best net lineup for that team, 
    then see if there's a 'Season Possessions' or 'Minutes' column 
    or some usage measure. We'll do a naive approach:
    Return the net rating + the 'Season Possessions' 
    to see if it's heavily used. 
    """
    tdf = df_lineup[df_lineup["Team"]==team_name]
    tdf = tdf.sort_values("Net", ascending=False).head(top_n)
    if not len(tdf):
        return 0
    # if there's "Season Possessions" col:
    if "Season Possessions" in tdf.columns:
        best_net = tdf.iloc[0]["Net"]
        poss = tdf.iloc[0]["Season Possessions"]
        # Weighted formula:
        overlap_score = best_net * (poss / 1000.0)  # just an arbitrary scaling
        return overlap_score
    else:
        # fallback: just net
        return float(tdf.iloc[0]["Net"])

def build_team_metrics(teams, df_skill, df_lineup):
    """
    Returns a dict => { 
      team_name: {
        "weighted_dpm": float,
        "sum_o": float, "sum_d": float,
        "momentum": float,
        "lineup_strength": float
      }, ...
    }
    """
    out = {}
    for team in teams:
        wdpm = compute_weighted_dpm(df_skill, team, top_n=8)
        so, sd = compute_off_def_splits(df_skill, team, top_n=8)
        mom = compute_momentum_score(df_skill, team)
        lu_str = compute_lineup_overlap_strength(df_lineup, team)
        out[team] = {
            "weighted_dpm": wdpm,
            "off_split": so,
            "def_split": sd,
            "momentum": mom,
            "lineup_strength": lu_str
        }
    return out
