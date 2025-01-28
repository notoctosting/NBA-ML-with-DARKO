**README: NBA Machine Learning Sports Betting with DARKO Integration**  

---

# NBA Sports Betting Using Machine Learning 🏀  

A machine learning AI to predict NBA game outcomes—**money lines** (winners) and **over/unders**—integrating **XGBoost** models with daily-scraped **DARKO** data. Builds off an original project by [kyleskom](https://github.com/kyleskom/NBA-Machine-Learning-Sports-Betting), expanded to include deeper synergy logic, advanced metrics (Weighted DPM, Off/Def splits, best lineups), and daily caching of scraped data.

Achieves ~69% accuracy on money lines and ~55% on under/overs (XGBoost). Outputs **expected value** (EV) for each team’s money line and optionally a **Kelly Criterion** fraction. We also incorporate **DARKO** (Daily Adjusted and Regressed Kalman Optimized) data for more robust synergy and clarity in final predictions.

---

## Features

1. **XGBoost** for Money Line & Over/Under predictions, updated daily.  
2. **Expected Value** & optional **Kelly Criterion** bet sizing, factoring in the model’s win probability vs. odds.  
3. **DARKO** daily data for more **accurate** synergy:  
   - Summed team points to see if it aligns with the Over/Under or the chosen side.  
   - Weighted DPM & Off/Def splits to highlight team strengths.  
   - Best lineup ratings to see top net rating lineups.  
   - Player-level daily insights (top scorers, etc.) to see who’s driving projected performance.  
4. **Caching** of daily-scraped data (one date-based CSV per day) to avoid repeated Selenium calls. Optionally force re-scrape if needed.  
5. **ASCII** color-coded synergy output:  
   - “Moneyline synergy” (XGBoost side vs. Darko side),  
   - “EV synergy” (whether the chosen side’s EV is positive),  
   - Weighted DPM, advanced stats, top scorers—**all** displayed for easy interpretation.  

---

## Packages Used

- **TensorFlow** (optional, if you want the old NN approach)  
- **XGBoost** – The main gradient boosting framework  
- **Numpy** – Scientific computing  
- **Pandas** – Data manipulation & analysis  
- **Colorama** – Color text output in console  
- **Tqdm** – Progress bars  
- **Requests** – HTTP library (for odds or other data)  
- **Scikit-learn** – Additional ML tools  
- **Selenium** & **webdriver_manager** – For scraping the DARKO Shiny app pages  

Python 3.11 is recommended.  

---

## Setup & Usage

1. **Clone** the repo and **install** dependencies:

```
git clone https://github.com/YOUR-REPO/NBA-ML-with-DARKO.git
cd NBA-ML-with-DARKO
pip3 install -r requirements.txt
```

2. **Fetching Odds / Running XGBoost**:
   - Example:
     ```
     python3 main.py -xgb -odds=betmgm
     ```
     This pulls the day’s betmgm odds from sbrodds if available, prompts the script to do XGBoost picks, and prints money lines, over/unders, expected value, etc.

3. **Scraping DARKO Data**:
   - By default, the script will attempt to scrape the **Daily** (Player Per-Game), **Lineup**, and **Current Skill** CSVs for the day.  
   - The **cache** is date-based: e.g., `darko_data/daily_projections_YYYYMMDD.csv`. If that file already exists, we skip re-scraping unless you pass `-force_dark`.

4. **Optional Flags**:
   - `-kc` => Show Kelly Criterion fraction on EV lines.  
   - `-force_dark` => Force re-scrape of Darko CSVs even if they exist.  

5. **Output**:
   - After XGBoost lines and EV, you’ll see a synergy block with color-coded ASCII boxes, showing:
     - XGBoost-chosen side & probability,  
     - EV for both sides,  
     - Darko daily sums (margin),  
     - “Moneyline synergy” (AGREE or DISAGREE) vs. Darko side,  
     - “EV synergy” (POSITIVE if your chosen side’s EV is > 0),  
     - Weighted DPM, Off/Def splits, best lineup rating,  
     - Top daily scorers from Darko’s player-level projections.  

---

## Example Output

```
------------------betmgm odds data------------------
Los Angeles Lakers (-235) @ Charlotte Hornets (195)
... [XGBoost Predictions & EV lines] ...

Daily Adjusted & Regressed Kalman Optimized - DARKO
Scraping daily data for 20250127 => darko_data/daily_projections_20250127.csv
Scraping lineup data for 20250127 => darko_data/lineup_projections_20250127.csv
Scraping skill data for 20250127 => darko_data/current_skill_20250127.csv

================================================================================

===== EXPANDED DARKO + XGBOOST ANALYSIS WITH PLAYER-LEVEL CONTEXT =====

--------------------------------------------------------------------------------
| [Charlotte Hornets] @ [Los Angeles Lakers]                                 |
--------------------------------------------------------------------------------
| XGB => side=HOME (home=58.3%, away=41.7%)                                  |
| EV => Los Angeles Lakers:-16.85, Charlotte Hornets:22.92                   |
| Darko => Los Angeles Lakers:102.2, Charlotte Hornets:107.5 (margin= -5.3 ) |
| Moneyline synergy => REDDISAGREE                                          |
| EV synergy => GREENPOSITIVE                                               |
--------------------------------------------------------------------------------
| Los Angeles Lakers => WDPM=  7.20, Off=  2.50, Def=  4.50, BestLU= 12.00    |
| Charlotte Hornets  => WDPM=  0.50, Off= -0.80, Def=  1.40, BestLU=  0.50    |
--------------------------------------------------------------------------------
| Top scorers Los Angeles Lakers: [LeBron James=28.5pts] [A. Davis=24.3pts]  |
| Top scorers Charlotte Hornets: [LaMelo Ball=25.9pts] [T. Rozier=23.1pts]   |
--------------------------------------------------------------------------------

... [other games displayed similarly] ...
```

---

## Flask Web App (Optional)

If you want to explore a **Flask** interface:

```
cd Flask
flask --debug run
```
This can be extended to display synergy data in a browser, though it’s primarily a console-based workflow.

---

## Data and Training Models

1. **Gather** the newest data:
   ```
   cd src/Process-Data
   python -m Get_Data
   python -m Get_Odds_Data
   python -m Create_Games
   ```
2. **Train** or re-train XGBoost models:
   ```
   cd ../Train-Models
   python -m XGBoost_Model_ML
   python -m XGBoost_Model_UO
   ```
3. Optionally do advanced synergy metrics with **DARKO** by scraping daily with:
   - `scrape_dark_data_for_date(teams, ...)` in your code.  

---

## Contributing

All contributions and improvements are welcomed—particularly around advanced synergy logic, new metrics from the DARKO data, or improved scraping reliability.

---

## License

This project is an **expanded** version of [kyleskom’s NBA-Machine-Learning-Sports-Betting](https://github.com/kyleskom/NBA-Machine-Learning-Sports-Betting). Feel free to clone/fork and propose changes. All standard disclaimers: this is **for educational** and informational use; **no** guarantee of profit or success. Bet responsibly.