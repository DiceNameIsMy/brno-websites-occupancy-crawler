import unittest
from unittest.mock import MagicMock, patch
from src.crawlers.luzanky import LuzankyCrawler
from src.crawlers.hangar import HangarCrawler


class TestLuzankyCrawler(unittest.TestCase):
    @patch("src.crawlers.base.webdriver.Chrome")
    def test_fetch_occupancy_success(self, mock_driver_cls):
        # Mock the driver and elements
        mock_driver = mock_driver_cls.return_value

        # Mock finding elements
        mock_element = MagicMock()
        mock_element.text = "BAZÉNY"

        mock_time_span = MagicMock()
        mock_time_span.text = "10/50"

        mock_element.find_element.return_value = mock_time_span
        mock_driver.find_elements.return_value = [mock_element]

        crawler = LuzankyCrawler()
        result = crawler.fetch_data(mock_driver)

        self.assertEqual(result, "10/50")

    @patch("src.crawlers.base.webdriver.Chrome")
    def test_fetch_occupancy_no_data(self, mock_driver_cls):
        mock_driver = mock_driver_cls.return_value
        mock_driver.find_elements.return_value = []

        crawler = LuzankyCrawler()
        result = crawler.fetch_data(mock_driver)

        self.assertIsNone(result)


class TestHangarCrawler(unittest.TestCase):
    @patch("src.crawlers.base.webdriver.Chrome")
    def test_fetch_occupancy_success(self, mock_driver_cls):
        mock_driver = mock_driver_cls.return_value

        # Mock finding the label element
        mock_label = MagicMock()

        # Mock parent element
        mock_parent = MagicMock()
        mock_parent.text = "Current occupancy Open! Plenty of space..."

        mock_label.find_element.return_value = mock_parent
        mock_driver.find_element.return_value = mock_label

        crawler = HangarCrawler()
        result = crawler.fetch_data(mock_driver)

        self.assertEqual(result, "Open! Plenty of space...")


if __name__ == "__main__":
    unittest.main()
