# NBA Sports Betting Using Machine Learning (with DARKO Integration)

A machine learning AI that predicts money line winners and under/overs of NBA games, now enhanced with additional **DARKO** data. Achieves ~69% accuracy on money lines and ~55% on under/overs. Outputs expected value (EV) for each side's money line, plus an optional fraction of your bankroll to wager based on the Kelly Criterion.

## What's New?

1. **Advanced Synergy Analysis**  
   - We now incorporate data from [DARKO](https://apanalytics.shinyapps.io/DARKO/): daily player per-game projections, lineups, and current player skill stats (DPM).  
   - Our code displays synergy between XGBoost picks and Darko’s daily margin, as well as whether the chosen side’s EV is positive or negative.  
   - We also highlight advanced metrics such as each team's Weighted DPM, Off/Def splits, and best lineup net ratings, plus top daily scorers from the Darko daily CSV.

2. **Caching Daily Scrapes**  
   - The scraper now caches each day’s CSV files (e.g., `daily_projections_YYYYMMDD.csv`) to avoid repeated Selenium calls on the same day.  
   - Use `-force_dark` or similar flags to override and re-scrape if needed.

3. **More Polished Console Output**  
   - Color-coded ASCII blocks help novices see synergy lines:  
     - “Moneyline synergy” (XGBoost side vs. Darko margin)  
     - “EV synergy” (chosen side’s EV > 0)  
   - Team-level metrics and top daily scorers are displayed with side-by-side data in easy-to-read sections.

---

## Packages Used

Use **Python 3.11**. Key packages:

- **XGBoost** for model predictions  
- **Tensorflow** (if using the neural network)  
- **Numpy** for scientific computing  
- **Pandas** for data manipulation  
- **Colorama** for colored text  
- **Tqdm** for optional progress bars  
- **Requests** for HTTP calls  
- **Scikit_learn** for ML utilities  
- **Selenium / webdriver_manager** for scraping the DARKO site  
- **Flask** (optional) if you want the web UI

Make sure all are in your `requirements.txt`.

---

## Usage

1. **Clone & Install**  
   ```
   git clone https://github.com/notoctosting/NBA-ML-with-DARKO.git
   cd NBA-ML-with-DARKO
   pip3 install -r requirements.txt
   ```

2. **XGBoost Predictions**  
   Run:
   ```
   python3 main.py -xgb -odds=fanduel
   ```
   or specify a different sportsbook: `-odds=betmgm`, `-odds=draftkings`, etc. If no `-odds` is given, you’ll be prompted to enter lines manually.

3. **Darko Scraping & Synergy**  
   - Add the `-darko` flag to scrape daily per-game projections, lineups, and current skill.  
   - By default, the code caches data to `darko_data/daily_projections_YYYYMMDD.csv` etc.  
   - Use `-force_dark` if you want to re-scrape the same day’s data.  
   - After scraping, the console prints synergy blocks that combine XGBoost picks, EV, and advanced Darko metrics.

4. **Kelly Criterion**  
   - Pass `-kc` to see how much of your bankroll to bet if you want to apply Kelly sizing.  
   - If you prefer a less risky approach, bet half the Kelly fraction.

---

## Example Commands

```
# XGBoost picks + synergy with Darko (scraping from betmgm lines)
python3 main.py -xgb -odds=betmgm -darko

# Force re-scrape Darko data
python3 main.py -xgb -odds=betmgm -darko -force_dark
```

---

## Interpretation of Output

1. **Money Line & Over/Under**:  
   Example lines:  
   ```
   Charlotte Hornets vs Los Angeles Lakers (58.3%): OVER 222.5 (61.1%)
   Charlotte Hornets EV: 22.92
   Los Angeles Lakers EV: -16.85
   ```
   - 58.3% chance for Hornets to win, plus an Over 222.5 pick at 61.1%.  
   - The Hornets side has positive EV while the Lakers side is negative.

2. **Enhanced Darko Synergy Block**:  
   - Prints each match in a color-coded ASCII table.  
   - Shows “Moneyline synergy => AGREE or DISAGREE” if XGB’s chosen side aligns with Darko’s daily margin.  
   - “EV synergy => POSITIVE or NEGATIVE” if the chosen side’s EV is above/below zero.  
   - Weighted DPM, Off/Def splits, best lineup rating, top daily scorers, etc., for each team.

---


## Getting New Data & Training Models

```
# Acquire the latest data for 2023-24 season
cd src/Process-Data
python -m Get_Data
python -m Get_Odds_Data
python -m Create_Games

# Train or retrain the XGBoost models
cd ../Train-Models
python -m XGBoost_Model_ML
python -m XGBoost_Model_UO
```

---
