# src/Utils/monte_carlo.py
import numpy as np

def simulate_monte_carlo(daily_player_df, stat_col="PTS", stdev_factor=0.15, n_sims=10000):
    """
    For each player, sample from Normal(mean=Darko stat, std=mean*stdev_factor).
    Summation => distribution for each team.
    Returns {team: np.array with simulated totals}
    """
    teams = daily_player_df["SearchTeam"].unique()
    results = {t: np.zeros(n_sims) for t in teams}

    means = daily_player_df[stat_col].astype(float).values
    team_assign = daily_player_df["SearchTeam"].values

    for sim_idx in range(n_sims):
        stds = means * stdev_factor
        draws = np.random.normal(loc=means, scale=stds)
        partial_sums = {}
        for i, val in enumerate(draws):
            tm = team_assign[i]
            partial_sums[tm] = partial_sums.get(tm, 0.0) + val

        for tm in teams:
            results[tm][sim_idx] = partial_sums.get(tm, 0.0,)

    return results
