# src/Utils/darko_scraper.py

import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException
import os
import datetime

def scrape_daily_player_projections_by_team(teams, output_csv="daily_projections.csv"):
    """
    (Unchanged) Old working code for Daily Player Per-Game Projections
    that filters each `team` in the global search box.
    """
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)

    try:
        url = "https://apanalytics.shinyapps.io/DARKO/"
        driver.get(url)

        # Click the "Daily Player Per-Game Projections" tab
        daily_tab = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Daily Player Per-Game Projections"))
        )
        daily_tab.click()

        # Wait for the table
        table_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.dataTable")))
        time.sleep(2)

        # Show 100 if possible
        try:
            show_entries_select = Select(driver.find_element(By.CSS_SELECTOR, "select[name='DataTables_Table_0_length']"))
            show_entries_select.select_by_visible_text("100")
            time.sleep(2)
        except:
            print("Warning: Could not find 'Show entries' dropdown on Daily tab.")

        # Grab headers
        header_cells = table_elem.find_elements(By.CSS_SELECTOR, "thead tr th")
        headers = [hc.text.strip() for hc in header_cells]
        final_headers = ["SearchTeam"] + headers

        # Overwrite CSV
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(final_headers)

        # Filter each team name
        for team in teams:
            search_input = driver.find_element(By.CSS_SELECTOR, "div#DataTables_Table_0_filter input[type='search']")
            search_input.clear()
            search_input.send_keys(team)
            time.sleep(2)

            table_elem = driver.find_element(By.CSS_SELECTOR, "table.dataTable")
            rows = table_elem.find_elements(By.CSS_SELECTOR, "tbody tr")

            rows_data = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                row_vals = [c.text.strip() for c in cells]
                if any(row_vals) and "No matching records" not in row_vals[0]:
                    rows_data.append(row_vals)

            # Append to CSV
            with open(output_csv, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for rv in rows_data:
                    writer.writerow([team] + rv)

        return output_csv

    finally:
        driver.quit()


def scrape_lineup_projections_by_team(teams, output_csv="lineup_projections.csv"):
    """
    Same logic as daily, but for "Lineup Projections" tab.
    We open the tab, set "Show 50/100" if possible, then for each `team` in `teams`,
    type that name in the global search, gather all rows, append to CSV with "SearchTeam" col.
    """
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)

    try:
        url = "https://apanalytics.shinyapps.io/DARKO/"
        driver.get(url)

        # Click "Lineup Projections"
        lineup_tab = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Lineup Projections"))
        )
        lineup_tab.click()

        # Wait for table
        table_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.dataTable")))
        time.sleep(2)

        # Attempt "Show 50" or "Show 100"
        try:
            show_entries_select = Select(driver.find_element(By.CSS_SELECTOR, "select[name='DataTables_Table_0_length']"))
            # We can pick 20, 50, or 100 if available
            show_entries_select.select_by_visible_text("50")
            time.sleep(2)
        except:
            print("Warning: Could not find 'Show entries' dropdown on Lineup tab.")

        # Grab headers
        header_cells = table_elem.find_elements(By.CSS_SELECTOR, "thead tr th")
        headers = [hc.text.strip() for hc in header_cells]
        final_headers = ["SearchTeam"] + headers

        # Overwrite CSV
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(final_headers)

        # For each team, type in global search
        for team in teams:
            search_input = driver.find_element(By.CSS_SELECTOR, "div#DataTables_Table_0_filter input[type='search']")
            search_input.clear()
            search_input.send_keys(team)
            time.sleep(2)

            # Re-locate rows
            table_elem = driver.find_element(By.CSS_SELECTOR, "table.dataTable")
            rows = table_elem.find_elements(By.CSS_SELECTOR, "tbody tr")

            rows_data = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                row_vals = [c.text.strip() for c in cells]
                if any(row_vals) and "No matching records" not in row_vals[0]:
                    rows_data.append(row_vals)

            # Append to CSV
            with open(output_csv, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for rv in rows_data:
                    writer.writerow([team] + rv)

        return output_csv

    finally:
        driver.quit()


def scrape_current_player_skill_by_team(teams, output_csv="current_skill.csv"):
    """
    Filters each team name on the 'Current Player Skill Projections' tab and appends rows to a CSV.
    Handles the StaleElementReferenceException by re-locating the table rows 
    after the DataTables processing is complete.
    """
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)

    try:
        url = "https://apanalytics.shinyapps.io/DARKO/"
        driver.get(url)

        # 1) Click the 'Current Player Skill Projections' tab
        skill_tab = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Current Player Skill Projections"))
        )
        skill_tab.click()

        # 2) Wait for table
        table_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.dataTable"))
        )
        time.sleep(2)

        # 3) (Optional) Attempt 'Show 50' or 'Show 100'
        try:
            show_entries_select = Select(driver.find_element(
                By.CSS_SELECTOR, 
                "select[name='DataTables_Table_0_length']"
            ))
            show_entries_select.select_by_visible_text("50")
            time.sleep(2)
        except:
            print("Warning: Could not find 'Show entries' dropdown on Skill tab.")

        # 4) Grab table headers
        header_cells = table_elem.find_elements(By.CSS_SELECTOR, "thead tr th")
        headers = [hc.text.strip() for hc in header_cells]
        final_headers = ["SearchTeam"] + headers

        # 5) Overwrite the CSV with a fresh header row
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(final_headers)

        # 6) For each team, filter & scrape
        for team in teams:
            # a) Type in the search box
            search_input = driver.find_element(
                By.CSS_SELECTOR, 
                "div#DataTables_Table_0_filter input[type='search']"
            )
            search_input.clear()
            search_input.send_keys(team)
            
            # b) Wait for DataTables to finish processing
            #    Typically there's a <div class="dataTables_processing" style="display: block;"> 
            #    we wait until it's invisible
            try:
                wait.until(
                    EC.invisibility_of_element_located(
                        (By.CSS_SELECTOR, "div.dataTables_processing[style*='display: block']")
                    )
                )
            except:
                pass
            
            time.sleep(1)  # small extra pause for safety
            
            # c) Now re-locate table rows to avoid stale references
            table_elem = driver.find_element(By.CSS_SELECTOR, "table.dataTable")
            rows = table_elem.find_elements(By.CSS_SELECTOR, "tbody tr")

            # d) Build a list of row values
            rows_data = []
            for row in rows:
                # We'll do a try/except in case of partial staleness:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    row_vals = [c.text.strip() for c in cells]
                    if any(row_vals) and "No matching records" not in row_vals[0]:
                        rows_data.append(row_vals)
                except StaleElementReferenceException:
                    # If stale, we can re-locate cells
                    # or skip
                    continue

            # e) Append them to CSV
            with open(output_csv, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for rv in rows_data:
                    writer.writerow([team] + rv)

        return output_csv

    finally:
        driver.quit()


def scrape_dark_data_for_date(teams, date_str=None, force_scrape=False, out_dir="Data/darko"):
    """
    A 'wrapper' that checks if we have today's CSV for daily, lineup, skill.
    If not, or if force_scrape=True, it calls the scraping functions.

    :param teams: list of team names
    :param date_str: e.g. '2025-01-27'. If None, use today's date
    :param force_scrape: bool, if True, forcibly scrape again
    :param out_dir: directory to store the CSV files (now defaults to Data/darko)
    :return: a dict of { 'daily': daily_csv_path, 'lineup': lineup_csv_path, 'skill': skill_csv_path }
    """

    if not date_str:
        date_str = datetime.date.today().strftime("%Y%m%d")

    # Create both Data and Data/darko directories if they don't exist
    if not os.path.exists("Data"):
        os.makedirs("Data")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # We'll define the final CSV paths
    daily_csv = os.path.join(out_dir, f"daily_projections_{date_str}.csv")
    lineup_csv = os.path.join(out_dir, f"lineup_projections_{date_str}.csv")
    skill_csv  = os.path.join(out_dir, f"current_skill_{date_str}.csv")

    # Check if they exist
    daily_exists = os.path.exists(daily_csv)
    lineup_exists = os.path.exists(lineup_csv)
    skill_exists = os.path.exists(skill_csv)

    # If file exists and not force_scrape => skip scraping
    if daily_exists and not force_scrape:
        print(f"Daily CSV for {date_str} already exists: {daily_csv}")
    else:
        print(f"Scraping daily data for {date_str} => {daily_csv}")
        scrape_daily_player_projections_by_team(teams, output_csv=daily_csv)

    if lineup_exists and not force_scrape:
        print(f"Lineup CSV for {date_str} already exists: {lineup_csv}")
    else:
        print(f"Scraping lineup data for {date_str} => {lineup_csv}")
        scrape_lineup_projections_by_team(teams, output_csv=lineup_csv)

    if skill_exists and not force_scrape:
        print(f"Skill CSV for {date_str} already exists: {skill_csv}")
    else:
        print(f"Scraping skill data for {date_str} => {skill_csv}")
        scrape_current_player_skill_by_team(teams, output_csv=skill_csv)

    return {
       "daily": daily_csv,
       "lineup": lineup_csv,
       "skill": skill_csv
    }