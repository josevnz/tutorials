import re
from time import sleep
from typing import Dict

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

EMPIRE_STATE_2013_RACE_RESULTS = "https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Results"


class EmpireStateScrapper:

    def __init__(self, headless: bool = True, load_wait: int = 5):
        options = Options()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.load_wait = load_wait
        self.driver.get(EMPIRE_STATE_2013_RACE_RESULTS)
        sleep(self.load_wait)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def navigate(self) -> Dict[str, str]:
        links = {}
        while True:
            """
            OuterHtml example:
            <a class="athName athName-display" style="display: block; font-size: 21px; line-height: 1.2em; color: rgb(74, 74, 74); text-decoration: none; width: 334px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-family: ProximaNovaBold;" href="/event/382111/results/Event/1062909/Course/2407855/Bib/19">Wai Ching Soh</a>
            """
            for a in self.driver.find_elements(By.TAG_NAME, "a"):
                href = a.get_attribute('href')
                if re.search('Bib', href):
                    links[a.text.strip()] = href.strip()
            """
            OuterHtml example:
            <button style="margin: 5px; padding: 12px 8px; color: rgb(0, 168, 227); background-color: rgb(255, 255, 255); border: 1px solid rgb(179, 193, 206); cursor: pointer;" value="1">&gt;</button>
            """
            # Brute force the depth of the next (>) click button
            button = None
            for i in range(6, 10):
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    # button = self.driver.find_element(By.CSS_SELECTOR, f"div:nth-child({i}) > button")
                    button = WebDriverWait(self.driver, 20).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, f"div:nth-child({i}) > button")))
                    break
                except NoSuchElementException:
                    pass
            if button and button.text == '>':
                # button.click()
                self.driver.execute_script("arguments[0].click();", button)
            else:
                break
        return links
