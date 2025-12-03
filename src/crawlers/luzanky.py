from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import BaseCrawler


class LuzankyCrawler(BaseCrawler):
    @property
    def source_name(self):
        return "luzanky"

    @property
    def url(self):
        return "https://bazenyluzanky.starez.cz/"

    def fetch_data(self, driver):
        driver.get(self.url)

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
                    print(f"[{self.source_name}] Error extracting text: {e}")
                    continue

        return None
