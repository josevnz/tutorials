import pprint
import re
from time import sleep
from typing import Any, List

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

EMPIRE_STATE_2013_RACE_RESULTS = "https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Results"


class RacerLinksScrapper:

    def __init__(self, headless: bool = True, load_wait: int = 5):
        self.rank_to_bib: list[int] = []
        options = Options()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.load_wait = load_wait
        self.driver.get(EMPIRE_STATE_2013_RACE_RESULTS)
        sleep(self.load_wait)
        self.racers = {}

    def __enter__(self):
        try:
            self.__get_racer_details__()
            self.__click__(6)
            self.__get_racer_details__()
            self.__click__(7)
            self.__get_racer_details__()
            self.__click__(7)
            self.__get_racer_details__()
            self.__click__(9)
            self.__get_racer_details__()
            self.__click__(9)
            self.__get_racer_details__()
            self.__click__(7)
            self.__get_racer_details__()
            self.__click__(7)
            self.__get_racer_details__()
        except NoSuchElementException as nse:
            raise ValueError("Error finding race details", nse)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def __get_racer_details__(self) -> None:
        """
        Not the most efficient way, but simple enough.
        First pass, get the racer names and link to racer details
        """
        for a in self.driver.find_elements(By.TAG_NAME, "a"):
            href = a.get_attribute('href')
            if re.search('Bib', href):
                name = a.text.strip().title()
                url = href.strip()
                bib = int(url.split('/')[-1])
                self.racers[bib] = {
                    "name": name,
                    "url": url,
                }

        """
        Next batch of details.
        Claim
        M 29
        Bib 19
        Kuala Lumpur, -, MYS
        Claim
        ...
        """
        record = {}
        count = 0
        for span in self.driver.find_elements(By.TAG_NAME, "span"):
            text = span.text.strip()
            if text == 'Claim':
                count += 1
            matcher = re.search('([A-Z])\\s(\\d+)', text)
            if matcher:
                record['Gender'] = matcher.group(1)
                record['Age'] = int(matcher.group(2))
            matcher = re.search('Bib\\s(\\d+)', text)
            if matcher:
                record['Bib'] = int(matcher.group(1))
                self.rank_to_bib.append(record['Bib'])
            matcher = re.search(',', text)
            if matcher:
                tokens = span.text.split(',')
                if len(tokens) == 3:
                    record['City'] = tokens[0]
                    record['State'] = tokens[1]
                    record['Country'] = tokens[2]
                elif len(tokens) == 2:
                    record['City'] = ""
                    record['State'] = tokens[0]
                    record['Country'] = tokens[1]
                else:
                    record['City'] = ""
                    record['State'] = ""
                    record['Country'] = tokens[0]
            # By now all the record parts should be available
            if 'Country' in record:
                bib = record['Bib']
                self.racers[bib]['Overall Rank'] = count
                if 'Gender' in record:
                    self.racers[bib]['Gender'] = record['Gender'].strip()
                else:
                    self.racers[bib]['Gender'] = ""
                if 'Age' in record:
                    self.racers[bib]['Age'] = record['Age']
                else:
                    self.racers[bib]['Age'] = ""
                self.racers[bib]['City'] = record['City'].strip()
                self.racers[bib]['State'] = record['State'].strip()
                self.racers[bib]['Country'] = record['Country'].strip()
                self.racers[bib]['Bib'] = bib
                record = {}

        """
        Last piece of information, get pace and race time (HH:MM:SS).
        Times are sorted by rank, match these with the rank_to_bib map.
        """
        sleep(1)
        times = []
        paces = []
        count = 0
        div = self.driver.find_element(By.TAG_NAME, "div")
        for text in div.text.split('\n'):
            if re.search('\\d+:\\d+$', text):
                time = text.strip()
                if (count % 2) == 0:
                    paces.append(time)
                else:
                    times.append(time)
                count += 1
        for count in range(0, len(times)):
            bib = self.rank_to_bib[count]
            pace = paces[count]
            time = times[count]
            self.racers[bib]['Full Race Time'] = time
            self.racers[bib]['Pace Time'] = pace

    def __click__(self, level: int) -> Any:
        button = WebDriverWait(self.driver, 20).until(
            expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, f"div:nth-child({level}) > button")))
        self.driver.execute_script("arguments[0].click();", button)
        sleep(2.5)
        return button


class RacerDetailsScrapper:

    def __init__(self, url: str, name: str, headless: bool = True, load_wait: int = 5):
        options = Options()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.load_wait = load_wait
        self.driver.get(url)
        sleep(self.load_wait)
        self.name = name

    def __enter__(self):
        self.__get_racer_details__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def __get_racer_details__(self):
        """
        This method is dense, because the data is scattered all over the place on the page
        """

        """
        Get Gender, Age, State
        Chip Start Time, Distance, Gun Time.
        """

        """
        Race splits for 20th, 65th and full course:
        split, Overall,Gender, Division, Pace, Time
        """
        pass
