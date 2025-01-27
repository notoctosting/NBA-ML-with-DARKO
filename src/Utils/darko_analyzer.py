# advanced_dark_analysis.py

import pandas as pd
from colorama import Fore, Style, init

def deep_dark_analysis(
    today_matches,
    xgb_out,       # e.g. { (home, away): {...} }
    darko_sums,    # e.g. { (home, away): (dh, da) }
    team_metrics,  # e.g. { team: { "weighted_dpm":..., "off_split":..., ... } }
    dpm_threshold=1.0
):
    """
    A synergy display that:
      - Prints XGBoost picks & EV
      - Prints Darko margin
      - Then shows advanced metrics from team_metrics
      - Color-coded synergy 
      - Provides comprehensive data that are known for correlation with real results
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
        darko_side = home if margin>=0 else away

        synergy_color = Fore.GREEN if (
            (xgb_side=="home" and margin>=0) or
            (xgb_side=="away" and margin<0)
        ) else Fore.RED
        synergy_msg = "AGREE" if synergy_color == Fore.GREEN else "DISAGREE"

        # Gather advanced metrics for each team
        home_m = team_metrics.get(home, {})
        away_m = team_metrics.get(away, {})

        # Build an ASCII block
        print(f"\n{'-'*65}")
        match_title = f"[{away}] @ [{home}]"
        print(f"| {Fore.YELLOW}{match_title:<61}{Style.RESET_ALL}|")
        print(f"{'-'*65}")
        # line 1: XGB side & EV
        # color EV
        home_ev_col = Fore.GREEN if ev_home>0 else Fore.RED
        away_ev_col = Fore.GREEN if ev_away>0 else Fore.RED

        xgb_text = f"XGB => side={xgb_side.upper()} (Hprob={home_prob*100:.1f}%, Aprob={away_prob*100:.1f}%)"
        ev_text = (f"EV => {home}:{home_ev_col}{ev_home:.2f}{Style.RESET_ALL}, "
                   f"{away}:{away_ev_col}{ev_away:.2f}{Style.RESET_ALL}")

        print(f"| {xgb_text:<63}|")
        print(f"| {ev_text:<63}|")

        # line 2: Darko total & synergy
        darko_txt = f"Darko => {home}:{dh:.1f}, {away}:{da:.1f} (margin={margin:.1f}, side={darko_side})"
        synergy_line = f"{synergy_color}{synergy_msg}{Style.RESET_ALL}"
        synergy_final = f"{darko_txt} => {synergy_line}"
        print(f"| {synergy_final:<63}|")

        # line 3: home advanced metrics
        # Weighted DPM, Off, Def, Momentum, lineup
        hw_dpm = home_m.get("weighted_dpm", 0)
        hw_off = home_m.get("off_split", 0)
        hw_def = home_m.get("def_split", 0)
        # hw_mom = home_m.get("momentum", 0)
        hw_line = home_m.get("lineup_strength", 0)

        adv_h = (f"{home} => WeightedDPM={hw_dpm:5.2f}, "
                 f"O={hw_off:5.2f}, D={hw_def:5.2f}, "
                 f"LUpStr={hw_line:4.1f}")
        print(f"{'-'*65}")
        print(f"| {adv_h:<63}|")

        # line 4: away advanced
        aw_dpm = away_m.get("weighted_dpm", 0)
        aw_off = away_m.get("off_split", 0)
        aw_def = away_m.get("def_split", 0)
        # aw_mom = away_m.get("momentum", 0)
        aw_line = away_m.get("lineup_strength", 0)

        adv_a = (f"{away} => WeightedDPM={aw_dpm:5.2f}, "
                 f"O={aw_off:5.2f}, D={aw_def:5.2f}, "
                 f"LUpStr={aw_line:4.1f}")
        print(f"| {adv_a:<63}|")

        print(f"{'-'*65}")

    print(f"{Fore.CYAN}\n===== END of DEEP DARK ANALYSIS ====={Style.RESET_ALL}")
