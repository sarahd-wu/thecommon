from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import time

def fetch_cookies(username, password):
    # Step 1: Open Shibboleth-protected page
    driver = webdriver.Chrome()
    driver.get("https://alumni.engage.amherst.edu/search")

    # Step 2: Enter username/password (auto)
    driver.find_element(By.NAME, "j_username").send_keys(username)
    driver.find_element(By.NAME, "j_password").send_keys(password + Keys.RETURN)

    # Step 3: Let the user manually handle Duo
    print("Please complete the Duo push or enter your 2FA code in the browser...")

    # Wait until login completes (or manually add a longer sleep)
    while "https://alumni.engage.amherst.edu/search" not in driver.current_url:
        time.sleep(1)

    # Step 4: Grab cookies after Duo completes
    csrf_token = csrf_token = driver.find_element(By.CSS_SELECTOR, 'meta[name="csrf-token"]').get_attribute("content")
    cookies = driver.get_cookies()
    driver.quit()

    return csrf_token, cookies