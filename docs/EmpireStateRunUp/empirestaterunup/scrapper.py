import pprint
import re
import subprocess
from time import sleep
from typing import Any, Dict

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

EMPIRE_STATE_2013_RACE_RESULTS = "https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Results"


class RacerLinksScrapper:

    def __init__(self, headless: bool = True, load_wait: int = 5, debug: bool = False):
        self.rank_to_bib: list[int] = []
        options = Options()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.load_wait = load_wait
        self.driver.get(EMPIRE_STATE_2013_RACE_RESULTS)
        sleep(self.load_wait)
        self.racers = {}
        self.debug = debug

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
        The following attributes are easier to fill by asking for a particular BIB
        Pace and race time (HH:MM:SS).
            Times are sorted by rank, match these with the rank_to_bib map.
        Race position: Overall, Gender, Division
            Some racers did not identify as Male or Female and their Gender position is missing.
        """

        if self.debug:
            print("Racers")
            pprint.pprint(self.racers)
            print("Rank to BIB")
            pprint.pprint(self.rank_to_bib)

    def __click__(self, level: int) -> Any:
        button = WebDriverWait(self.driver, 20).until(
            expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, f"div:nth-child({level}) > button")))
        self.driver.execute_script("arguments[0].click();", button)
        sleep(2.5)
        return button


class RacerDetailsScrapper:

    def __init__(self, racer: Dict[str, Any], headless: bool = True, load_wait: int = 5, debug_level: int = 0):
        options = Options()
        fp = webdriver.FirefoxProfile()
        service = webdriver.FirefoxService()
        if headless:
            options.add_argument("--headless")
            if debug_level > 1:
                """
                Workaround for: `driver.get_log()`
                https://github.com/mozilla/geckodriver/issues/330
                """
                fp.set_preference("devtools.console.stdout.content", "true")
                options.log.level = "trace"
                service.log_output = subprocess.STDOUT
        options.profile = fp
        self.driver = webdriver.Firefox(
            options=options,
            service=service
        )
        self.load_wait = load_wait
        self.driver.get(racer['url'])
        sleep(self.load_wait)
        self.racer = racer
        self.debug_level = debug_level

    def __enter__(self):
        self.__get_racer_details__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def __get_racer_details__(self):
        """
        Race splits for 20th, 65th and full course:
        split, Overall,Gender, Division, Pace, Time
        """
        # Assume racer didn't finish
        self.racer['Overall Split 20th floor'] = ""
        self.racer['Gender Split 20th floor'] = ""
        self.racer['Bracket Split 20th floor'] = ""
        self.racer['Pace 20th floor'] = ""
        self.racer['Time 20th floor'] = ""
        self.racer['Overall Split 65th floor'] = ""
        self.racer['Gender Split 65th floor'] = ""
        self.racer['Bracket Split 65th floor'] = ""
        self.racer['Pace 65th floor'] = ""
        self.racer['Time 65th floor'] = ""
        self.racer['Overall Split Full Course'] = ""
        self.racer['Gender Split Full Course'] = ""
        self.racer['Bracket Split Full Course'] = ""
        self.racer['Pace Full Course'] = ""
        self.racer['Time Full Course'] = ""
        for div in self.driver.find_elements(By.CSS_SELECTOR, "div[class='row mx-0']"):
            value = div.text.strip()
            if self.debug_level > 0:
                print(value)
            """
            Parsing is pretty brittle, several assumptions where made:
                * Should get 3 rows of 3 columns, except for runners who did not finish the full course
            """
            values = value.split('\n')
            if values[0] == '20th Floor' and values[1] != '--':
                self.racer['Overall Split 20th floor'] = values[1]
                self.racer['Gender Split 20th floor'] = values[3]
                self.racer['Bracket Split 20th floor'] = values[5]
                self.racer['Pace 20th floor'] = values[7]
                self.racer['Time 20th floor'] = values[9]
            elif values[0] == '65th Floor' and values[1] != '--':
                self.racer['Overall Split 65th floor'] = values[1]
                self.racer['Gender Split 65th floor'] = values[3]
                self.racer['Bracket Split 65th floor'] = values[5]
                self.racer['Pace 65th floor'] = values[7]
                self.racer['Time 65th floor'] = values[9]
            elif values[0] == 'Full Course' and values[1] != '--':
                self.racer['Overall Split Full Course'] = values[1]
                self.racer['Gender Split Full Course'] = values[3]
                self.racer['Bracket Split Full Course'] = values[5]
                self.racer['Pace Full Course'] = values[7]
                self.racer['Time Full Course'] = values[9]
