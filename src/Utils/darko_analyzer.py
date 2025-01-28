# advanced_dark_analysis.py

import pandas as pd
from colorama import Fore, Style, init
from src.Utils import Kelly_Criterion as kc
def deep_dark_analysis(
    today_matches,
    xgb_out,       # e.g. { (home, away): {...} }
    darko_sums,    # e.g. { (home, away): (dh, da) }
    team_metrics,  # e.g. { team: { "weighted_dpm":..., "off_split":..., ... } }
    dpm_threshold=1.0,
    odds_data=None,
    kelly_criterion=False  # New parameter
):
    """
    Enhanced synergy display that separates:
    1. Moneyline synergy (XGB side matches Darko side)
    2. EV synergy (XGB-chosen side has positive EV)
    3. Kelly Criterion allocation when -kc flag is passed
    """
    init(autoreset=True)
    print(f"\n{Fore.CYAN}{'='*68}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}\n===== DEEP DARK (DARKO + XGBOOST) ANALYSIS ====={Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}{'='*68}{Style.RESET_ALL}")

    for (home, away) in today_matches:
        # XGB Info
        xinfo = xgb_out.get((home, away), {})
        xgb_side = xinfo.get("winner_side", "N/A")
        home_prob = xinfo.get("home_prob", 0.0)
        away_prob = xinfo.get("away_prob", 0.0)
        ev_home = xinfo.get("ev_home", 0.0)
        ev_away = xinfo.get("ev_away", 0.0)

        # Darko sums
        (dh, da) = darko_sums.get((home, away), (0, 0))
        margin = dh - da
        darko_side = "home" if margin >= 0 else "away"

        # Determine Moneyline Synergy
        ml_synergy = xgb_side == darko_side
        ml_color = Fore.GREEN if ml_synergy else Fore.RED
        ml_msg = "AGREE" if ml_synergy else "DISAGREE"

        # Determine EV Synergy (based on XGB's chosen side)
        chosen_ev = ev_home if xgb_side == "home" else ev_away
        ev_synergy = chosen_ev > 0
        ev_color = Fore.GREEN if ev_synergy else Fore.RED
        ev_msg = "POSITIVE" if ev_synergy else "NEGATIVE"

        # Get odds if available
        odds_str = ""
        if odds_data and f"{home}:{away}" in odds_data:
            game_odds = odds_data[f"{home}:{away}"]
            home_ml = game_odds[home]["money_line_odds"]
            away_ml = game_odds[away]["money_line_odds"]
            total = game_odds["under_over_odds"]
            odds_str = f" (ML: {away} {away_ml:>4} @ {home} {home_ml:>4}, O/U: {total})"

        # Build ASCII block
        print(f"\n{'-'*65}")
        match_title = f"[{away} {away_ml:>4}] @ [{home} {home_ml:>4}]"
        print(f"| {Fore.YELLOW}{match_title:<61}{Style.RESET_ALL}|")
        
        print(f"{'-'*65}")
        # XGB prediction & probabilities
        xgb_text = f"XGB => side={xgb_side.upper()} (Hprob={home_prob*100:.1f}%, Aprob={away_prob*100:.1f}%)"
        print(f"| {xgb_text:<63}|")

        # Synergy lines
        ml_synergy_text = f"Moneyline Synergy: {ml_color}{ml_msg}{Style.RESET_ALL}"
        ev_synergy_text = f"EV Synergy: {ev_color}{ev_msg}{Style.RESET_ALL}"
        print(f"| {ml_synergy_text:<63}|")
        print(f"| {ev_synergy_text:<63}|")

        # Darko margin
        darko_txt = f"Darko => {home}:{dh:.1f}, {away}:{da:.1f} (margin={margin:.1f})"
        print(f"| {darko_txt:<63}|")

        # Expected Values (color-coded) with Kelly
        home_ev_col = Fore.GREEN if ev_home > 0 else Fore.RED
        away_ev_col = Fore.GREEN if ev_away > 0 else Fore.RED
        
        # Get Kelly percentages if available
        kelly_home = kelly_away = None
        if kelly_criterion and odds_data and f"{home}:{away}" in odds_data:
            game_odds = odds_data[f"{home}:{away}"]
            home_odds = game_odds[home]["money_line_odds"]
            away_odds = game_odds[away]["money_line_odds"]
            kelly_home = kc.calculate_kelly_criterion(home_odds, home_prob)
            kelly_away = kc.calculate_kelly_criterion(away_odds, away_prob)

        # Format EV text with optional Kelly
        if kelly_criterion:
            ev_text = (f"EV => {home}:{home_ev_col}{ev_home:.2f}{Style.RESET_ALL} "
                      f"(Kelly: {kelly_home:.1f}%), "
                      f"{away}:{away_ev_col}{ev_away:.2f}{Style.RESET_ALL} "
                      f"(Kelly: {kelly_away:.1f}%)")
        else:
            ev_text = (f"EV => {home}:{home_ev_col}{ev_home:.2f}{Style.RESET_ALL}, "
                      f"{away}:{away_ev_col}{ev_away:.2f}{Style.RESET_ALL}")
        
        print(f"| {ev_text:<63}|")

        # Advanced Metrics
        print(f"{'-'*65}")
        # Home team metrics
        home_m = team_metrics.get(home, {})
        hw_dpm = home_m.get("weighted_dpm", 0)
        hw_off = home_m.get("off_split", 0)
        hw_def = home_m.get("def_split", 0)
        hw_line = home_m.get("lineup_strength", 0)

        adv_h = (f"{home} => WeightedDPM={hw_dpm:5.2f}, "
                f"O={hw_off:5.2f}, D={hw_def:5.2f}, "
                f"LUpStr={hw_line:4.1f}")
        print(f"| {adv_h:<63}|")

        # Away team metrics
        away_m = team_metrics.get(away, {})
        aw_dpm = away_m.get("weighted_dpm", 0)
        aw_off = away_m.get("off_split", 0)
        aw_def = away_m.get("def_split", 0)
        aw_line = away_m.get("lineup_strength", 0)

        adv_a = (f"{away} => WeightedDPM={aw_dpm:5.2f}, "
                f"O={aw_off:5.2f}, D={aw_def:5.2f}, "
                f"LUpStr={aw_line:4.1f}")
        print(f"| {adv_a:<63}|")
        print(f"{'-'*65}")

    print(f"{Fore.CYAN}\n===== END of DEEP DARK ANALYSIS ====={Style.RESET_ALL}")
