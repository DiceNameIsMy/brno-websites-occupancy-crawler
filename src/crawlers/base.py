import abc
import csv
import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class BaseCrawler(abc.ABC):
    def __init__(self, data_dir="data"):
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            data_dir,
        )
        self.csv_file = os.path.join(self.data_dir, f"{self.source_name}.csv")

    @property
    @abc.abstractmethod
    def source_name(self):
        pass

    @property
    @abc.abstractmethod
    def url(self):
        pass

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    @abc.abstractmethod
    def fetch_data(self, driver):
        pass

    def log_to_csv(self, data):
        if not data:
            print(f"[{self.source_name}] No data found.")
            return

        timestamp = datetime.datetime.now().isoformat()
        file_exists = os.path.isfile(self.csv_file)
        os.makedirs(self.data_dir, exist_ok=True)

        with open(self.csv_file, "a", newline="") as csvfile:
            fieldnames = ["timestamp", "occupancy"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({"timestamp": timestamp, "occupancy": data})
            print(f"[{self.source_name}] Logged: {timestamp}, {data}")

    def run(self):
        driver = None
        try:
            driver = self.setup_driver()
            data = self.fetch_data(driver)
            self.log_to_csv(data)
        except Exception as e:
            print(f"[{self.source_name}] An error occurred: {e}")
        finally:
            if driver:
                driver.quit()
