# src/Utils/simulate_injury.py
from itertools import product

def simulate_lineups(daily_player_df, questionable_players):
    """
    For each questionable player: in or out => scenario.
    scenario_df, scenario_prob
    'name', 'prob_in', 'minutes_scale'
    """
    if not questionable_players:
        return [(daily_player_df.copy(), 1.0)]

    all_scenarios = []
    n = len(questionable_players)

    for combo in product([True, False], repeat=n):
        scenario_copy = daily_player_df.copy()
        scenario_prob = 1.0

        for i, is_in in enumerate(combo):
            p_info = questionable_players[i]
            name = p_info["name"]
            prob_in = p_info["prob_in"]
            scale = p_info.get("minutes_scale", 1.0)

            if is_in:
                scenario_prob *= prob_in
                scenario_copy.loc[scenario_copy["Player"] == name, "PTS"] *= scale
                scenario_copy.loc[scenario_copy["Player"] == name, "Minutes"] *= scale
            else:
                scenario_prob *= (1 - prob_in)
                scenario_copy.loc[scenario_copy["Player"] == name, ["PTS","Minutes"]] = 0

        if scenario_prob > 0:
            all_scenarios.append((scenario_copy, scenario_prob))

    return all_scenarios
