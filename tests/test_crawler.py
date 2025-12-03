import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


def test_fetch_pool_occupancy(driver):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    url = "https://bazenyluzanky.starez.cz/"
    driver.get(url)

    # Wait for the element to be present
    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#info-ticket-collapse .col.area.person")
        )
    )

    # Logic to find the element:
    # Find all divs with class 'col area person'
    # Check which one contains "BAZÉNY"
    # Get the span with class 'time' inside it

    elements = driver.find_elements(
        By.CSS_SELECTOR, "#info-ticket-collapse .col.area.person"
    )
    occupancy_text = None

    for el in elements:
        # Use get_attribute("textContent") to get text including hidden
        # if any, though .text should work if visible.
        if "BAZÉNY" in el.text:
            try:
                time_span = el.find_element(By.CSS_SELECTOR, "span.time")
                occupancy_text = time_span.text
                break
            except Exception:
                continue

    assert occupancy_text is not None, "Could not find occupancy text for BAZÉNY"
    print(f"Found occupancy: {occupancy_text}")

    # Verify format "number/number"
    assert re.match(r"^\d+/\d+$", occupancy_text), (
        f"Occupancy text '{occupancy_text}' " "does not match format 'number/number'"
    )
