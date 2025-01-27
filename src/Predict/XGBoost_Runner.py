import copy

import numpy as np
import pandas as pd
import xgboost as xgb
from colorama import Fore, Style, init, deinit
from src.Utils import Expected_Value
from src.Utils import Kelly_Criterion as kc


# from src.Utils.Dictionaries import team_index_current
# from src.Utils.tools import get_json_data, to_data_frame, get_todays_games_json, create_todays_games
init()
xgb_ml = xgb.Booster()
xgb_ml.load_model('Models/XGBoost_Models/XGBoost_68.7%_ML-4.json')
xgb_uo = xgb.Booster()
xgb_uo.load_model('Models/XGBoost_Models/XGBoost_53.7%_UO-9.json')

def build_xgb_dict(games, ml_predictions, ev_results):
    xgb_out = {}
    for i, (home, away) in enumerate(games):
        ml = ml_predictions[i]
        ev = ev_results[i]
        xgb_out[(home, away)] = {
            "winner_side": ml["winner_side"],
            "home_prob": ml["home_prob"],
            "away_prob": ml["away_prob"],
            "ev_home": ev["ev_home"],
            "ev_away": ev["ev_away"]
        }
    return xgb_out

def xgb_runner(data, todays_games_uo, frame_ml, games, home_team_odds, away_team_odds, kelly_criterion):
    ml_predictions_array = []

    for row in data:
        ml_predictions_array.append(xgb_ml.predict(xgb.DMatrix(np.array([row]))))

    frame_uo = copy.deepcopy(frame_ml)
    frame_uo['OU'] = np.asarray(todays_games_uo)
    data = frame_uo.values
    data = data.astype(float)

    ou_predictions_array = []

    for row in data:
        ou_predictions_array.append(xgb_uo.predict(xgb.DMatrix(np.array([row]))))
    ml_info_list = []   ### NEW CODE ###
    count = 0
    for game in games:
        home_team = game[0]
        away_team = game[1]
        ml_array = ml_predictions_array[count]  # shape => [[away_prob, home_prob]]
        away_prob = ml_array[0][0]
        home_prob = ml_array[0][1]
        winner_idx = 1 if home_prob >= away_prob else 0

        # under/over
        ou_array = ou_predictions_array[count]  # shape => [[under_prob, over_prob, or depends? we have 3 classes if U/O?
        under_over = int(np.argmax(ou_array[0]))  # 2 classes => 0=under,1=over?
        
        if winner_idx == 1:
            # home wins
            winner_confidence = round(home_prob * 100, 1)
            if under_over == 0:
                un_confidence = round(ou_array[0][0]*100, 1)
                print(
                    Fore.GREEN + home_team + Style.RESET_ALL + Fore.CYAN + f" ({winner_confidence}%)" 
                    + Style.RESET_ALL + ' vs ' + Fore.RED + away_team + Style.RESET_ALL 
                    + ': ' + Fore.MAGENTA + 'UNDER ' + Style.RESET_ALL + str(todays_games_uo[count]) 
                    + Style.RESET_ALL + Fore.CYAN + f" ({un_confidence}%)" + Style.RESET_ALL
                )
            else:
                over_conf = round(ou_array[0][1]*100,1)
                print(
                    Fore.GREEN + home_team + Style.RESET_ALL + Fore.CYAN + f" ({winner_confidence}%)" 
                    + Style.RESET_ALL + ' vs ' + Fore.RED + away_team + Style.RESET_ALL 
                    + ': ' + Fore.BLUE + 'OVER ' + Style.RESET_ALL + str(todays_games_uo[count]) 
                    + Style.RESET_ALL + Fore.CYAN + f" ({over_conf}%)" + Style.RESET_ALL
                )
            # also store in ml_info_list
            ml_info_list.append({
                "winner_side": "home",
                "home_prob": float(home_prob),
                "away_prob": float(away_prob)
            })
        else:
            # away wins
            winner_confidence = round(away_prob * 100, 1)
            if under_over == 0:
                un_confidence = round(ou_array[0][0]*100,1)
                print(
                    Fore.RED + home_team + Style.RESET_ALL + ' vs ' + Fore.GREEN + away_team + Style.RESET_ALL 
                    + Fore.CYAN + f" ({winner_confidence}%)" + Style.RESET_ALL 
                    + ': ' + Fore.MAGENTA + 'UNDER ' + Style.RESET_ALL + str(todays_games_uo[count]) 
                    + Style.RESET_ALL + Fore.CYAN + f" ({un_confidence}%)" + Style.RESET_ALL
                )
            else:
                over_conf = round(ou_array[0][1]*100,1)
                print(
                    Fore.RED + home_team + Style.RESET_ALL + ' vs ' + Fore.GREEN + away_team + Style.RESET_ALL 
                    + Fore.CYAN + f" ({winner_confidence}%)" + Style.RESET_ALL 
                    + ': ' + Fore.BLUE + 'OVER ' + Style.RESET_ALL + str(todays_games_uo[count]) 
                    + Style.RESET_ALL + Fore.CYAN + f" ({over_conf}%)" + Style.RESET_ALL
                )
            ml_info_list.append({
                "winner_side": "away",
                "home_prob": float(home_prob),
                "away_prob": float(away_prob)
            })

        count += 1


    if kelly_criterion:
        print("------------Expected Value & Kelly Criterion-----------")
    else:
        print("---------------------Expected Value--------------------")

    # PASS 2: EV lines
    ev_results = []
    count = 0
    for game in games:
        home_team, away_team = game[0], game[1]
        away_prob = ml_predictions_array[count][0][0]
        home_prob = ml_predictions_array[count][0][1]
        ev_home = ev_away = 0
        if home_team_odds[count] and away_team_odds[count]:
            ev_home = float(Expected_Value.expected_value(home_prob, int(home_team_odds[count])))
            ev_away = float(Expected_Value.expected_value(away_prob, int(away_team_odds[count])))

        home_color = Fore.GREEN if ev_home>0 else Fore.RED
        away_color = Fore.GREEN if ev_away>0 else Fore.RED

        ev_results.append({
            "ev_home": ev_home,
            "ev_away": ev_away
        })

        if kelly_criterion:
            frac_home = kc.calculate_kelly_criterion(home_team_odds[count], home_prob)
            frac_away = kc.calculate_kelly_criterion(away_team_odds[count], away_prob)
            print(f"{home_team} EV: {home_color}{ev_home}{Style.RESET_ALL}, Kelly fraction: {frac_home}%")
            print(f"{away_team} EV: {away_color}{ev_away}{Style.RESET_ALL}, Kelly fraction: {frac_away}%")
        else:
            print(f"{home_team} EV: {home_color}{ev_home}{Style.RESET_ALL}")
            print(f"{away_team} EV: {away_color}{ev_away}{Style.RESET_ALL}")

        count += 1

    print("-------------------------------------------------------")

    # Now build final dictionary: we have ml_info_list and ev_results, each same length as games
    xgb_dict = build_xgb_dict(games, ml_info_list, ev_results)  ### FIXED => pass ml_info_list
    deinit()
    return xgb_dict







# def xgb_runner(data, todays_games_uo, frame_ml, games, home_team_odds, away_team_odds, kelly_criterion):
#     ml_predictions_array = []
#     for row in data:
#         # shape => [[away_prob, home_prob]]
#         preds = xgb_ml.predict(xgb.DMatrix(np.array([row])))
#         ml_predictions_array.append(preds)

#     frame_uo = copy.deepcopy(frame_ml)
#     frame_uo['OU'] = np.asarray(todays_games_uo)
#     data_uo = frame_uo.values.astype(float)

#     ou_predictions_array = []
#     for row in data_uo:
#         ou_preds = xgb_uo.predict(xgb.DMatrix(np.array([row])))
#         ou_predictions_array.append(ou_preds)

#     # --- PASS 1: Print the XGB predictions as before, 
#     #     but also build ml_info_list with dicts for each game
#     ml_info_list = []   ### NEW CODE ###
#     count = 0
#     for game in games:
#         home_team, away_team = game[0], game[1]
#         ml_array = ml_predictions_array[count]  # shape => [[away_prob, home_prob]]
#         away_prob = ml_array[0][0]
#         home_prob = ml_array[0][1]
#         winner_idx = int(np.argmax(ml_array[count]))  # This is suspicious => we might do int(np.argmax(ml_array[0]))

#         # Actually let's do:
#         # winner_idx = 1 if home_prob >= away_prob else 0
#         winner_idx = 1 if home_prob >= away_prob else 0

#         # under/over
#         ou_array = ou_predictions_array[count]  # shape => [[under_prob, over_prob, or depends? we have 3 classes if U/O?
#         under_over = int(np.argmax(ou_array[0]))  # 2 classes => 0=under,1=over?

#         if winner_idx == 1:
#             # home wins
#             winner_confidence = round(home_prob * 100, 1)
#             if under_over == 0:
#                 un_confidence = round(ou_array[0][0]*100, 1)
#                 print(
#                     Fore.GREEN + home_team + Style.RESET_ALL + Fore.CYAN + f" ({winner_confidence}%)" 
#                     + Style.RESET_ALL + ' vs ' + Fore.RED + away_team + Style.RESET_ALL 
#                     + ': ' + Fore.MAGENTA + 'UNDER ' + Style.RESET_ALL + str(todays_games_uo[count]) 
#                     + Style.RESET_ALL + Fore.CYAN + f" ({un_confidence}%)" + Style.RESET_ALL
#                 )
#             else:
#                 over_conf = round(ou_array[0][1]*100,1)
#                 print(
#                     Fore.GREEN + home_team + Style.RESET_ALL + Fore.CYAN + f" ({winner_confidence}%)" 
#                     + Style.RESET_ALL + ' vs ' + Fore.RED + away_team + Style.RESET_ALL 
#                     + ': ' + Fore.BLUE + 'OVER ' + Style.RESET_ALL + str(todays_games_uo[count]) 
#                     + Style.RESET_ALL + Fore.CYAN + f" ({over_conf}%)" + Style.RESET_ALL
#                 )
#             # also store in ml_info_list
#             ml_info_list.append({
#                 "winner_side": "home",
#                 "home_prob": float(home_prob),
#                 "away_prob": float(away_prob)
#             })
#         else:
#             # away wins
#             winner_confidence = round(away_prob * 100, 1)
#             if under_over == 0:
#                 un_confidence = round(ou_array[0][0]*100,1)
#                 print(
#                     Fore.RED + home_team + Style.RESET_ALL + ' vs ' + Fore.GREEN + away_team + Style.RESET_ALL 
#                     + Fore.CYAN + f" ({winner_confidence}%)" + Style.RESET_ALL 
#                     + ': ' + Fore.MAGENTA + 'UNDER ' + Style.RESET_ALL + str(todays_games_uo[count]) 
#                     + Style.RESET_ALL + Fore.CYAN + f" ({un_confidence}%)" + Style.RESET_ALL
#                 )
#             else:
#                 over_conf = round(ou_array[0][1]*100,1)
#                 print(
#                     Fore.RED + home_team + Style.RESET_ALL + ' vs ' + Fore.GREEN + away_team + Style.RESET_ALL 
#                     + Fore.CYAN + f" ({winner_confidence}%)" + Style.RESET_ALL 
#                     + ': ' + Fore.BLUE + 'OVER ' + Style.RESET_ALL + str(todays_games_uo[count]) 
#                     + Style.RESET_ALL + Fore.CYAN + f" ({over_conf}%)" + Style.RESET_ALL
#                 )
#             ml_info_list.append({
#                 "winner_side": "away",
#                 "home_prob": float(home_prob),
#                 "away_prob": float(away_prob)
#             })

#         count += 1
