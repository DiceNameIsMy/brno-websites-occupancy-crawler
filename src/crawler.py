import csv
import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
URL = "https://bazenyluzanky.starez.cz/"
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)
CSV_FILE = os.path.join(DATA_DIR, "occupancy.csv")


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def fetch_occupancy(driver):
    driver.get(URL)

    # Wait for the element
    wait = WebDriverWait(driver, 20)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#info-ticket-collapse .col.area.person")
        )
    )

    elements = driver.find_elements(
        By.CSS_SELECTOR, "#info-ticket-collapse .col.area.person"
    )

    for el in elements:
        if "BAZÉNY" in el.text:
            try:
                time_span = el.find_element(By.CSS_SELECTOR, "span.time")
                return time_span.text
            except Exception as e:
                print(f"Error extracting text: {e}")
                continue

    return None


def log_to_csv(occupancy):
    if not occupancy:
        print("No occupancy data found.")
        return

    timestamp = datetime.datetime.now().isoformat()

    # Parse occupancy to separate current and max? Or just keep as string?
    # User asked to "append this data", implying the raw string or parsed.
    # Let's keep it simple: timestamp, occupancy_string

    file_exists = os.path.isfile(CSV_FILE)

    os.makedirs(DATA_DIR, exist_ok=True)

    with open(CSV_FILE, "a", newline="") as csvfile:
        fieldnames = ["timestamp", "occupancy"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({"timestamp": timestamp, "occupancy": occupancy})
        print(f"Logged: {timestamp}, {occupancy}")


def main():
    driver = None
    try:
        driver = setup_driver()
        occupancy = fetch_occupancy(driver)
        if occupancy:
            log_to_csv(occupancy)
        else:
            print("Failed to fetch occupancy.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
