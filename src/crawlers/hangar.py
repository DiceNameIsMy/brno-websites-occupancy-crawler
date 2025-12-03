from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import BaseCrawler


class HangarCrawler(BaseCrawler):
    @property
    def source_name(self):
        return "hangar"

    @property
    def url(self):
        return "https://hangarbrno.cz/en/home/"

    def fetch_data(self, driver):
        driver.get(self.url)

        # Wait for the element containing "Current occupancy"
        wait = WebDriverWait(driver, 20)
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Current occupancy')]")
            )
        )

        try:
            # Find the element with "Current occupancy"
            label_element = driver.find_element(
                By.XPATH, "//*[contains(text(), 'Current occupancy')]"
            )

            # The state is likely in a text node following the element or its parents.
            # We need to traverse up until we find a container that has more text than just the label.
            current_element = label_element
            full_text = current_element.text

            # Traverse up to 3 levels to find the container with the status text
            for _ in range(3):
                try:
                    parent = current_element.find_element(By.XPATH, "..")
                    parent_text = parent.text
                    # If parent has more text (and it's not just whitespace difference), use it
                    if (
                        len(parent_text.strip()) > len(full_text.strip()) + 5
                    ):  # +5 for "Open!" or similar
                        full_text = parent_text
                        current_element = parent
                        break
                    current_element = parent
                    full_text = parent_text
                except Exception:
                    break

            # Normalize text for comparison
            text_upper = full_text.strip().upper()

            # If the text is just "CURRENT OCCUPANCY", try to find a sibling of the current container
            if text_upper == "CURRENT OCCUPANCY":
                try:
                    next_sibling = current_element.find_element(
                        By.XPATH, "following-sibling::*"
                    )
                    return next_sibling.text
                except Exception:
                    pass

            # If text contains "CURRENT OCCUPANCY", extract the part after it
            if "CURRENT OCCUPANCY" in text_upper:
                idx = text_upper.find("CURRENT OCCUPANCY")
                # Return the part after it from the original string
                return full_text[idx + len("Current occupancy") :].strip()

            return full_text

        except Exception as e:
            print(f"[{self.source_name}] Error extracting text: {e}")
            return None
