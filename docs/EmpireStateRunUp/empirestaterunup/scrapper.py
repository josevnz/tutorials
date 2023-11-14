import re
from time import sleep
from typing import Dict, Any

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

EMPIRE_STATE_2013_RACE_RESULTS = "https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Results"


class RacerLinksScrapper:

    def __init__(self, headless: bool = True, load_wait: int = 5):
        options = Options()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.load_wait = load_wait
        self.driver.get(EMPIRE_STATE_2013_RACE_RESULTS)
        sleep(self.load_wait)
        self.__links = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def __get_racer_links__(self) -> None:
        for a in self.driver.find_elements(By.TAG_NAME, "a"):
            href = a.get_attribute('href')
            if re.search('Bib', href):
                name = a.text.strip().title()
                self.__links[name] = href.strip()

    def __click__(self, level: int) -> Any:
        button = WebDriverWait(self.driver, 20).until(
            expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, f"div:nth-child({level}) > button")))
        self.driver.execute_script("arguments[0].click();", button)
        sleep(2.5)
        return button

    def get_all_links(self) -> Dict[str, str]:
        self.__get_racer_links__()
        self.__click__(6)
        self.__get_racer_links__()
        self.__click__(7)
        self.__get_racer_links__()
        self.__click__(7)
        self.__get_racer_links__()
        self.__click__(9)
        self.__get_racer_links__()
        self.__click__(9)
        self.__get_racer_links__()
        self.__click__(7)
        self.__get_racer_links__()
        self.__click__(7)
        self.__get_racer_links__()
        return self.__links
