import time
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from colorama import Fore, init

init(autoreset=True)

from linkedin import LinkedIn

# Load config from setup.ini
config = configparser.ConfigParser()
config.read("setup.ini")

USERNAME = config.get("LinkedIn", "username")
PASSWORD = config.get("LinkedIn", "password")
PROFILE_URL = config.get("Target", "profile_url")
INCLUDE_NOTE = config.getboolean("Settings", "include_note", fallback=False)
MESSAGE = config.get("Settings", "message", fallback="")


def main():
    options = Options()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Uncomment for headless mode

    driver = webdriver.Chrome(options=options)

    client = LinkedIn(driver)

    try:
        client.selenium_login(USERNAME, PASSWORD)
        emails = client.singleScan_selenium(PROFILE_URL)
        print(Fore.GREEN + f"Final emails found: {emails}")
    finally:
        print(Fore.CYAN + "[INFO] Closing browser.")
        time.sleep(2)
        driver.quit()


if __name__ == "__main__":
    main()
