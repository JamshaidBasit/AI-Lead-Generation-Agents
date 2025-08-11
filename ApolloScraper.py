import csv
import json
import os
import re
import time
from datetime import datetime
import undetected_chromedriver as uc
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# --- Configuration ---
# Use a relative path or a configurable constant
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apollo_data")
# --- End Configuration ---


# --- Selenium Setup with User Profile ---
options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
options.add_argument("--window-size=1920,1080")
driver = uc.Chrome(options=options)
driver.implicitly_wait(5)
# --- End Selenium Setup ---


def wait_for_captcha(driver):
    """If CAPTCHA is detected, wait for manual solve."""
    try:
        captcha_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src,'recaptcha')]"))
        )
        if captcha_element:
            print("\n⚠ CAPTCHA detected! Please solve it manually in the browser...")
            input("Press Enter here after solving CAPTCHA...")
            # After solving, wait for the page to redirect
            WebDriverWait(driver, 10).until_not(EC.url_contains("login"))
    except TimeoutException:
        pass


def build_start_url():
    """Asks user for search filters and builds Apollo URL."""
    base_url = "https://app.apollo.io/#/people?page=1&sortAscending=false&sortByField=recommendations_score"

    job_title = input("Enter Job Title (leave blank to skip): ").strip()
    location = input("Enter Location (leave blank to skip): ").strip()

    if job_title:
        # Use URL encoding for spaces and other special characters
        base_url += f"&personTitles[]={job_title.replace(' ', '%20')}"
    if location:
        base_url += f"&personLocations[]={location.replace(' ', '%20')}"

    print(f"\n🔍 Generated Search URL: {base_url}\n")
    return base_url


def check_and_login(driver, config):
    """Checks if the user is logged in. If not, waits for manual login."""
    print('Checking login status...')
    driver.get('https://app.apollo.io/#/prospects')

    try:
        # Wait for the URL to change to the prospects page
        WebDriverWait(driver, 10).until(
            EC.url_contains("apollo.io/#/prospects")
        )
        print("✅ Already logged in.")
        driver.get(config['start_url'])
        return True
    except TimeoutException:
        print("🔑 Not logged in. Please log in manually...")
        driver.get('https://apollo.io/#/login')

        # Wait a reasonable amount of time for the user to login
        time.sleep(5)
        wait_for_captcha(driver)

        try:
            # Wait for successful login, up to a very long timeout
            WebDriverWait(driver, 9999).until(
                EC.url_contains("apollo.io/#/prospects")
            )
            print("✅ Login successful.")
            driver.get(config['start_url'])
            return True
        except TimeoutException:
            print("❌ Login timed out. Please try again.")
            return False


def find_and_copy_email(driver):
    """Finds and extracts email addresses from popup."""
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'zp_SZG4_')]"))
        )
        popup_container = driver.find_element(By.XPATH, "//div[contains(@class, 'zp_SZG4_')]")
        spans = popup_container.find_elements(By.TAG_NAME, "span")
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = [span.text for span in spans if email_pattern.match(span.text)]
        return emails
    except Exception as e:
        print(f"Failed to copy email: {str(e)}")
        return None


def next_page(driver):
    """Clicks 'next page' button and waits for the page to refresh."""
    try:
        # Wait for the next page button to be clickable
        next_page_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='right-arrow']"))
        )

        # Check if the button is disabled (last page)
        if "cursor-not-allowed" in next_page_button.get_attribute("class"):
            print("✅ Last page reached.")
            return False

        next_page_button.click()
        print("➡ Next page...")

        # Wait for the URL to change or the table to reload
        time.sleep(2)
        return True
    except TimeoutException:
        print("✅ No more pages or next page button not found.")
        return False
    except NoSuchElementException:
        print("✅ No more pages.")
        return False


def split_name(name):
    """Splits full name."""
    parts = name.split()
    return parts[0] if parts else '', ' '.join(parts[1:]) if len(parts) > 1 else ''


def write_to_csv(config, first_name, last_name, job_title, company_name, location, email_address1, email_address2, linkedin_url):
    """Writes data to CSV."""
    csv_file_path = config['export_file_name']
    date_now = datetime.now().strftime("%Y-%m-%d")
    headers = ['first_name', 'last_name', 'job_title', 'company_name', 'location', 'email_address1', 'email_address2', 'linkedin_url', 'date']
    data_row = [first_name, last_name, job_title, company_name, location, email_address1, email_address2, linkedin_url, date_now]

    # Check if file exists to write header only once
    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(data_row)


def main(driver):
    # Ensure config.json exists or create a default one
    config_file_path = 'config.json'
    if not os.path.exists(config_file_path):
        with open(config_file_path, 'w') as f:
            json.dump({"export_file_name": "apollo_leads.csv"}, f)

    with open(config_file_path, 'r') as file:
        config = json.load(file)

    # Build dynamic URL from user input
    config['start_url'] = build_start_url()

    if not check_and_login(driver, config):
        print("❌ Script terminated due to failed login.")
        # driver.quit()
        return

    try:
        while True:
            print("⏳ Waiting for the data to load...")
            try:
                # Wait for the main table container to be present
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy-loaded='true']"))
                )
                loaded_section = driver.find_element(By.CSS_SELECTOR, "[data-cy-loaded='true']")
                
                # New: Wait for at least one tbody element to appear inside the loaded section
                WebDriverWait(loaded_section, 20).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'tbody'))
                )
                
                tbodies = loaded_section.find_elements(By.TAG_NAME, 'tbody')
            except (TimeoutException, NoSuchElementException) as e:
                print("⚠ Timed out waiting for table to load. Retrying next page...")
                if not next_page(driver):
                    break
                continue

            if not tbodies:
                print("⚠ No data to process on this page.")
                break

            for tbody in tbodies:
                first_name, last_name, linkedin_url, job_title, company_name, location, email_address1, email_address2 = "", "", "", "", "", "", "", ""
                
                try:
                    # Extract name and LinkedIn URL
                    name_link = tbody.find_element(By.TAG_NAME, 'a')
                    first_name, last_name = split_name(name_link.text)
                    linkedin_url = name_link.get_attribute('href')
                except NoSuchElementException:
                    print("❌ Could not find name/linkedin link.")
                    continue
                
                try:
                    # Extract job title and location
                    job_title_location_elements = tbody.find_elements(By.CLASS_NAME, 'zp_Y6y8d')
                    if len(job_title_location_elements) >= 2:
                        job_title = job_title_location_elements[0].text
                        location = job_title_location_elements[1].text
                except NoSuchElementException:
                    print("❌ Could not find job title or location.")
                    pass

                try:
                    # Extract company name
                    company_link = tbody.find_element(By.XPATH, ".//a[contains(@href, 'accounts') or contains(@href, 'organizations')]")
                    company_name = company_link.text
                except NoSuchElementException:
                    print("❌ Could not find company name.")
                    pass

                try:
                    # Click email button and extract emails
                    email_button = tbody.find_element(By.CSS_SELECTOR, "span.zp_gKxYk")
                    email_button.click()
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".zp-button.zp_zUY3r.zp_r4MyT.zp_LZAms.zp_jRaZ5")))
                    email_addresses = find_and_copy_email(driver)
                    
                    if email_addresses:
                        email_address1 = email_addresses[0] if len(email_addresses) > 0 else ''
                        email_address2 = email_addresses[1] if len(email_addresses) > 1 else ''
                    
                    # Close the popup by clicking the button again
                    email_button.click()
                except Exception as e:
                    print(f"❌ Email extraction error: {e}")
                    time.sleep(1)
                    continue

                write_to_csv(config, first_name, last_name, job_title, company_name, location, email_address1, email_address2, linkedin_url)
                print(f"✅ Processed: {first_name} {last_name} | {job_title} | {company_name} | {email_address1}")

            if not next_page(driver):
                break

    except WebDriverException as e:
        print(f"❌ A critical WebDriver error occurred: {str(e)}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {str(e)}")
    finally:
        print("\n--- Script finished. ---")
        # driver.quit()  # This line is commented out to keep the browser open.


if __name__ == "__main__":
    main(driver)




###https://app.apollo.io/#/people?page=1&sortAscending=false&sortByField=recommendations_score&personTitles[]=project%20manager