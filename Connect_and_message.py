import time
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import Fore, init

init(autoreset=True)

# Read credentials and settings from setup.ini
config = configparser.ConfigParser()
config.read("setup.ini")
USERNAME = config.get("LinkedIn", "username")
PASSWORD = config.get("LinkedIn", "password")
PROFILE_URL = config.get("Target", "profile_url")
INCLUDE_NOTE = config.getboolean("Settings", "include_note")
MESSAGE = config.get("Settings", "message")


def login_to_linkedin(driver):
    print(Fore.CYAN + "[INFO] Logging into LinkedIn...")
    driver.get("https://www.linkedin.com/login")

    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    password_input = driver.find_element(By.ID, "password")

    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)

    sign_in_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    sign_in_button.click()
    time.sleep(3)
    print(Fore.GREEN + "[INFO] Logged in successfully!")


def send_connection_request(driver, profile_url, include_note, message):
    print(Fore.YELLOW + f"[INFO] Opening profile: {profile_url}")
    driver.get(profile_url)
    time.sleep(3)

    try:
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        connect_buttons = [btn for btn in all_buttons if btn.text.strip() == "Connect"]

        if connect_buttons:
            for btn in connect_buttons:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(2)

                    if not include_note:
                        send = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send now']"))
                        )
                        driver.execute_script("arguments[0].click();", send)
                        print(Fore.GREEN + "[INFO] Connection request sent without note.")
                    else:
                        add_note_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Add a note"]'))
                        )
                        add_note_btn.click()

                        message_box = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//textarea[@name="message"]'))
                        )
                        message_box.send_keys(message)

                        send_invite_button = driver.find_element(By.XPATH, '//button[@aria-label="Send invitation"]')
                        driver.execute_script("arguments[0].click();", send_invite_button)
                        print(Fore.GREEN + "[INFO] Connection request sent with note.")

                    break  # Successfully sent request, exit loop
                except Exception as e:
                    print(Fore.RED + f"[ERROR] Failed to send request: {e}")
                    continue
        else:
            print(Fore.LIGHTYELLOW_EX + "[INFO] Connect button not found, trying to follow the profile...")

            follow_buttons = [btn for btn in all_buttons if btn.text.strip() == "Follow"]
            if follow_buttons:
                try:
                    follow_btn = follow_buttons[0]
                    driver.execute_script("arguments[0].scrollIntoView(true);", follow_btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", follow_btn)
                    print(Fore.GREEN + "[INFO] Followed the profile successfully.")
                except Exception as e:
                    print(Fore.RED + f"[ERROR] Could not follow the profile: {e}")
            else:
                print(Fore.RED + "[ERROR] Neither Connect nor Follow button found.")

    except Exception as e:
        print(Fore.RED + f"[ERROR] Could not process the profile: {e}")


def main():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    try:
        login_to_linkedin(driver)
        send_connection_request(driver, PROFILE_URL, INCLUDE_NOTE, MESSAGE)
    finally:
        print(Fore.CYAN + "[INFO] Closing browser.")
        time.sleep(2)
        driver.quit()


if __name__ == "__main__":
    main()
