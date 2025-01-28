# advanced_dark_analysis.py

import pandas as pd
from colorama import Fore, Style, init
from src.Utils import Kelly_Criterion as kc
def deep_dark_analysis(
    today_matches,
    xgb_out,       
    darko_sums,    
    team_metrics,  
    dpm_threshold=1.0,
    odds_data=None,
    kelly_criterion=False
):
    """
    Enhanced synergy display that separates:
    1. Moneyline synergy (XGB side matches Darko side)
    2. EV synergy (XGB-chosen side has positive EV)
    3. Kelly Criterion allocation when -kc flag is passed
    """
    init(autoreset=True)
    border = "=" * 80
    separator = "-" * 80
    
    print(f"\n{Fore.CYAN}{border}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'DEEP DARK (DARKO + XGBOOST) ANALYSIS':^80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{border}{Style.RESET_ALL}\n")

    for (home, away) in today_matches:
        # Get all the same data as before
        xinfo = xgb_out.get((home, away), {})
        xgb_side = xinfo.get("winner_side", "N/A")
        home_prob = xinfo.get("home_prob", 0.0)
        away_prob = xinfo.get("away_prob", 0.0)
        ev_home = xinfo.get("ev_home", 0.0)
        ev_away = xinfo.get("ev_away", 0.0)
        
        (dh, da) = darko_sums.get((home, away), (0, 0))
        margin = dh - da
        darko_side = "home" if margin >= 0 else "away"
        
        # Format game header
        if odds_data and f"{home}:{away}" in odds_data:
            game_odds = odds_data[f"{home}:{away}"]
            home_ml = game_odds[home]["money_line_odds"]
            away_ml = game_odds[away]["money_line_odds"]
            total = game_odds["under_over_odds"]
            match_title = f"[{away} {away_ml:>4}] @ [{home} {home_ml:>4}] (O/U: {total:>6})"
        else:
            match_title = f"{away} @ {home}"

        print(f"{separator}")
        print(f"|{Fore.YELLOW}{match_title:^78}{Style.RESET_ALL}|")
        print(f"{separator}")

        # XGB & Probabilities line
        xgb_text = f"XGB Pick: {xgb_side.upper()} (Home: {home_prob*100:.1f}%, Away: {away_prob*100:.1f}%)"
        print(f"|{xgb_text:^78}|")

        # Darko daily sums
        darko_text = f"Darko: {darko_side.upper()} (Home: {dh}, Away: {da})"
        print(f"|{darko_text:^78}|")

        # Synergy lines (centered)
        ml_synergy = xgb_side == darko_side
        ml_color = Fore.GREEN if ml_synergy else Fore.RED
        ml_msg = "AGREE" if ml_synergy else "DISAGREE"
        ml_text = f"ML Synergy: {ml_color}{ml_msg:^8}{Style.RESET_ALL}"
        print(f"|{ml_text:^78}|")

        # metric to show that the underdog is the side with positive EV and if darko and xgb agree on the underdog to the same degree - may need some calculations



        # EV line (centered with colors)
        ev_text = f"EV: {home} ({Fore.GREEN if ev_home > 0 else Fore.RED}{ev_home:>6.2f}{Style.RESET_ALL}) | " \
                 f"{away} ({Fore.GREEN if ev_away > 0 else Fore.RED}{ev_away:>6.2f}{Style.RESET_ALL})"
        print(f"|{ev_text:^78}|")

        # Kelly line if enabled
        if kelly_criterion and odds_data and f"{home}:{away}" in odds_data:
            game_odds = odds_data[f"{home}:{away}"]
            home_odds = game_odds[home]["money_line_odds"]
            away_odds = game_odds[away]["money_line_odds"]
            kelly_home = kc.calculate_kelly_criterion(home_odds, home_prob)
            kelly_away = kc.calculate_kelly_criterion(away_odds, away_prob)
            kelly_text = f"Kelly: {home} ({kelly_home:>5.1f}%) | {away} ({kelly_away:>5.1f}%)"
            print(f"|{kelly_text:^78}|")

        print(f"{separator}")

        # Team Metrics (aligned in columns)
        for team, label in [(home, "HOME"), (away, "AWAY")]:
            metrics = team_metrics.get(team, {})
            dpm = metrics.get("weighted_dpm", 0)
            off = metrics.get("off_split", 0)
            def_val = metrics.get("def_split", 0)
            lineup = metrics.get("lineup_strength", 0)
            
            metrics_text = f"{team:.<25} DPM: {dpm:>6.2f} | Off: {off:>6.2f} | Def: {def_val:>6.2f} | BestLU: {lineup:>6.2f}"
            print(f"|{metrics_text:^78}|")

        print(f"{separator}\n")

    print(f"{Fore.CYAN}{border}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'END OF DEEP DARK ANALYSIS':^80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{border}{Style.RESET_ALL}\n")
