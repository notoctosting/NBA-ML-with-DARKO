
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
from colorama import Fore, Style, init

def scrape_daily_player_projections_by_team(teams, output_csv="daily_projections.csv"):
    """
    Uses Selenium to:
      - Open the DARKO site
      - Click "Daily Player Per-Game Projections"
      - Increase "Show entries" to 100 (optional)
      - Filter by each team name in the global search box
      - Scrape the resulting rows into a CSV.

    Returns the path to the CSV for further processing.
    """

    # 1) Set up Selenium (Chrome) with webdriver_manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)  # up to 20s wait for elements

    try:
        # 2) Navigate to the main DARKO page
        url = "https://apanalytics.shinyapps.io/DARKO/"
        driver.get(url)

        # 3) Click the "Daily Player Per-Game Projections" tab
        daily_tab = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Daily Player Per-Game Projections"))
        )
        daily_tab.click()

        # 4) Wait for the table to appear
        table_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.dataTable"))
        )
        time.sleep(2)  # small pause so data fully loads

        # 5) (Optional) Increase "Show entries" to 100 to reduce pagination
        #    May fail if table ID changes. Adjust if needed or skip if happy with 30 rows.
        try:
            show_entries_select = Select(driver.find_element(
                By.CSS_SELECTOR, "select[name='DataTables_Table_0_length']"
            ))
            show_entries_select.select_by_visible_text("100")
            time.sleep(2)  # wait for table to reload
        except:
            print("Warning: Could not find 'Show entries' dropdown. Possibly a different table ID?")

        # 6) Grab column headers once (for the CSV)
        header_cells = table_elem.find_elements(By.CSS_SELECTOR, "thead tr th")
        headers = [hc.text.strip() for hc in header_cells]
        # We'll prepend a "SearchTeam" column to indicate which team was typed in the search box
        final_headers = ["SearchTeam"] + headers

        # 7) Overwrite the CSV with a fresh header row
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(final_headers)

        # 8) For each team in `teams`, filter & scrape
        for team in teams:
            # print(f"\nFiltering by team name: '{team}'")

            # 8a) Find the global search box (in dataTables_filter)
            #     Typically has `aria-controls="DataTables_Table_0"`.
            search_input = driver.find_element(
                By.CSS_SELECTOR, "div#DataTables_Table_0_filter input[type='search']"
            )

            # 8b) Clear, then type the team name
            search_input.clear()
            search_input.send_keys(team)

            # 8c) Wait a bit for DataTables to refresh
            time.sleep(2)

            # 8d) Re-locate table rows
            table_elem = driver.find_element(By.CSS_SELECTOR, "table.dataTable")
            rows = table_elem.find_elements(By.CSS_SELECTOR, "tbody tr")

            # 8e) Build a list of row values
            rows_data = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                row_values = [c.text.strip() for c in cells]
                # Omit empty or "No matching records found"
                if any(row_values) and "No matching records" not in row_values[0]:
                    rows_data.append(row_values)

            # 8f) Append them to our CSV
            with open(output_csv, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for row_vals in rows_data:
                    writer.writerow([team] + row_vals)

            # print(f"  --> Found {len(rows_data)} rows for '{team}'")

        return output_csv

    finally:
        # 9) Close the browser
        driver.quit()


def analyze_scraped_data(csv_path, today_matches):
    """
    Loads the scraped CSV (with 'SearchTeam' and other columns) into pandas,
    does a simple grouping on total PTS by team, and prints color-highlighted
    results to console. 
    """
    # print("\n--- Performing Basic Analysis on Scraped Data ---")

    # 1) Load into a DataFrame
    df = pd.read_csv(csv_path)

    # 2) Because headers can vary or sometimes be empty strings, let's find
    #    the exact column name that contains "PTS." 
    #    If we trust it's exactly "PTS," we can skip this. 
    #    Otherwise, do a quick "fuzzy" match:
    pts_col = None
    for col in df.columns:
        if "PTS" in col.upper():
            pts_col = col
            break
    if not pts_col:
        print("Could not find a 'PTS' column. Check the scraped headers!")
        print("Available columns:", df.columns.tolist())
        return

    # 3) Convert that column to numeric (in case it's strings)
    df[pts_col] = pd.to_numeric(df[pts_col], errors='coerce')

    # 4) Group by 'SearchTeam' and sum the PTS
    group = df.groupby("SearchTeam")[pts_col].sum().reset_index()
    group.columns = ["Team", "Total_PTS"]

    # 5) Highlight the highest total PTS by printing it in green (console)
    max_pts = group["Total_PTS"].max()
    init(autoreset=True)  # colorama init


    # format for teams playing eachother today and the projected points 
    print("\n --- Teams Playing Each Other Today ---")
    for match in today_matches:
        team1 = match[0]
        team2 = match[1]
        team1_pts = group.loc[group["Team"] == team1, "Total_PTS"].values[0]
        team2_pts = group.loc[group["Team"] == team2, "Total_PTS"].values[0]

        if team1_pts > team2_pts:
            print(f"{Fore.GREEN}{team1:<20}{Style.RESET_ALL} {team1_pts:.1f} vs {Fore.RED}{team2:<20}{Style.RESET_ALL} {team2_pts:.1f}")
        else:
            print(f"{Fore.RED}{team1:<20}{Style.RESET_ALL} {team1_pts:.1f} vs {Fore.GREEN}{team2:<20}{Style.RESET_ALL} {team2_pts:.1f}")

        