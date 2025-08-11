import time
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import Fore, init

init(autoreset=True)

class LinkedIn:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
        else:
            self.driver = None

    def selenium_login(self, username, password):
        if not self.driver:
            raise Exception("Selenium WebDriver not initialized")
        print(Fore.CYAN + "[INFO] Logging into LinkedIn...")
        self.driver.get("https://www.linkedin.com/login")

        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_input = self.driver.find_element(By.ID, "password")

        username_input.send_keys(username)
        password_input.send_keys(password)

        sign_in_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
        sign_in_button.click()

        time.sleep(5)
        print(Fore.GREEN + "[INFO] Logged in successfully!")

    def singleScan_selenium(self, profile_url):
        if not self.driver:
            raise Exception("Selenium WebDriver not initialized")
        url = profile_url.rstrip('/') + "/overlay/contact-info/"
        print(Fore.YELLOW + f"[INFO] Opening contact info page: {url}")
        self.driver.get(url)

        time.sleep(5)  # Wait for page to load

        page_source = self.driver.page_source

        # ✅ Extract all emails
        emails_found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_source)
        unique_emails = list(set(emails_found))

        # ✅ Filter only .com emails
        valid_emails = [email for email in unique_emails if email.lower().endswith('.com')]

        # ✅ Extract name from <title>
        soup = BeautifulSoup(page_source, "html.parser")
        try:
            name = soup.find("title").text.strip().split(" | ")[0]
        except:
            name = "Name not found"

        # ✅ Return list of (name, email) tuples
        results = [(name, email) for email in valid_emails]

        print(Fore.GREEN + f"[INFO] Contacts found (Name, Email): {results}")
        return results
