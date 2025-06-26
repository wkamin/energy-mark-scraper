import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

# --- CONFIGURATION ---
LOGIN_URL = "https://darcypartners.com/innovators?topics=%5B%2212%22%5D"  # TODO: Replace with your login URL
USERNAME = "your_username"                # TODO: Replace with your username
PASSWORD = "your_password"                # TODO: Replace with your password
TABLE_CONTAINER_SELECTOR = ".ag-center-cols-viewport"  # Adjust if needed
ROW_SELECTOR = ".ag-row"
SCROLL_PAUSE_TIME = 1
MAX_ROWS_TO_PROCESS = 5  # Set to -1 to process all rows, or any positive integer to limit

# --- SETUP ---
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(LOGIN_URL)

time.sleep(2)  # Wait for page to load

# --- LOGIN (customize as needed) ---
# Example login (uncomment and adjust selectors as needed):
# driver.find_element(By.ID, "username").send_keys(USERNAME)
# driver.find_element(By.ID, "password").send_keys(PASSWORD)
# driver.find_element(By.ID, "login-button").click()
# time.sleep(5)  # Wait for login to complete

# --- NAVIGATE TO TABLE PAGE IF NEEDED ---
# TODO: Add navigation if your table is not on the landing page after login

time.sleep(2)  # Wait for table to load

SCROLLABLE_SELECTOR = ".ag-body-vertical-scroll-viewport"

try:
    scrollable = driver.find_element(By.CSS_SELECTOR, SCROLLABLE_SELECTOR)
    print(f"Found scrollable element: {SCROLLABLE_SELECTOR}")
except NoSuchElementException:
    raise Exception(f"Could not find the scrollable table element: {SCROLLABLE_SELECTOR}")

# Get row height (use a fallback if not found)
try:
    first_row = driver.find_element(By.CSS_SELECTOR, ROW_SELECTOR)
    row_height = first_row.size['height']
except Exception:
    row_height = 44  # fallback

SCROLL_ROWS = 20  # number of rows to scroll at a time

all_row_ids = set()
all_row_data = []
max_scrolls = 1000
scroll_attempts_without_new_rows = 0
max_attempts_without_new_rows = 10

actions = ActionChains(driver)

rows_processed = 0

for i in range(max_scrolls):
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, ROW_SELECTOR)
        new_row_found = False
        for row in rows:
            if MAX_ROWS_TO_PROCESS != -1 and rows_processed >= MAX_ROWS_TO_PROCESS:
                print(f"Reached the maximum number of rows to process: {MAX_ROWS_TO_PROCESS}")
                break
            try:
                row_id = row.get_attribute("row-id")
                if row_id and row_id not in all_row_ids:
                    all_row_ids.add(row_id)
                    # Company name and link
                    company_cell = row.find_element(By.CSS_SELECTOR, '.ag-cell[col-id="company.name"]')
                    company = company_cell.text
                    try:
                        company_link = company_cell.find_element(By.TAG_NAME, "a").get_attribute("href")
                    except NoSuchElementException:
                        company_link = ""
                    # Hover to get description (tooltip)
                    description = ""
                    try:
                        actions.move_to_element(company_cell).perform()
                        time.sleep(0.5)
                        # Try to extract the ::before pseudo-element content using JavaScript
                        content = driver.execute_script(
                            "return window.getComputedStyle(arguments[0], '::before').getPropertyValue('content');",
                            company_cell
                        )
                        if content and content != 'none' and content != '""':
                            description = content.strip('"')
                        else:
                            description = ""
                    except Exception:
                        description = ""
                    # Other columns
                    service_lines = row.find_element(By.CSS_SELECTOR, '.ag-cell[col-id="serviceLines"]').text
                    topic_tags = row.find_element(By.CSS_SELECTOR, '.ag-cell[col-id="topicTags"]').text
                    relevant_research = row.find_element(By.CSS_SELECTOR, '.ag-cell[col-id="isVendorMaterialsShown"]').text
                    featured_in_darcy = row.find_element(By.CSS_SELECTOR, '.ag-cell[col-id="lastFeaturedInDarcyLiveAt"]').text
                    all_row_data.append([
                        company, company_link, description, service_lines, topic_tags, relevant_research, featured_in_darcy
                    ])
                    new_row_found = True
                    rows_processed += 1
            except StaleElementReferenceException:
                # If a row goes stale, skip it this round
                continue

        if MAX_ROWS_TO_PROCESS != -1 and rows_processed >= MAX_ROWS_TO_PROCESS:
            print(f"Reached the maximum number of rows to process: {MAX_ROWS_TO_PROCESS}")
            break

        print(f"Scroll {i}: {len(all_row_ids)} unique rows found.")

        if new_row_found:
            scroll_attempts_without_new_rows = 0
        else:
            scroll_attempts_without_new_rows += 1

        if scroll_attempts_without_new_rows >= max_attempts_without_new_rows:
            print("No new rows found after several scrolls. Stopping.")
            break

        # Scroll the vertical scrollbar by 20 rows at a time
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollTop + arguments[1];",
            scrollable, row_height * SCROLL_ROWS
        )
        time.sleep(SCROLL_PAUSE_TIME)
    except StaleElementReferenceException:
        # If the whole set of rows goes stale, just continue to next scroll
        continue

print(f"Extracted {len(all_row_data)} unique rows.")

# Optionally, save to CSV
import csv
with open("extracted_table.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    for row in all_row_data:
        writer.writerow(row)

print("Saved to extracted_table.csv")
driver.quit() 