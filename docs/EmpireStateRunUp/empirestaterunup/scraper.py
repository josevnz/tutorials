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

from empirestaterunup.data import RaceFields, Level

EMPIRE_STATE_2013_RACE_RESULTS = "https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Results"


class RacerLinksScraper:

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
                    RaceFields.NAME.value: name,
                    RaceFields.URL.value: url
                }

        """
        Next batch of details.
        Claim
        M 29
        Bib 19
        Kuala Lumpur, -, MYS
        Claim
        ...
        Gender and age may be missing from the racers details ...
        """
        record = {
            RaceFields.GENDER.value: "",
            RaceFields.AGE.value: ""
        }
        count = 0
        for span in self.driver.find_elements(By.TAG_NAME, "span"):
            text = span.text.strip()
            if text == 'Claim':
                count += 1
            matcher = re.search('([A-Z])\\s(\\d+)', text)
            if matcher:
                record[RaceFields.GENDER.value] = matcher.group(1)
                record[RaceFields.AGE.value] = int(matcher.group(2))
            matcher = re.search('Bib\\s(\\d+)', text)
            if matcher:
                record[RaceFields.BIB.value] = int(matcher.group(1))
                self.rank_to_bib.append(record[RaceFields.BIB.value])
            matcher = re.search(',', text)
            if matcher:
                tokens = span.text.split(',')
                if len(tokens) == 3:
                    record[RaceFields.CITY.value] = tokens[0]
                    record[RaceFields.STATE.value] = tokens[1]
                    record[RaceFields.COUNTRY.value] = tokens[2]
                elif len(tokens) == 2:
                    record[RaceFields.CITY.value] = ""
                    record[RaceFields.STATE.value] = tokens[0]
                    record[RaceFields.COUNTRY.value] = tokens[1]
                else:
                    record[RaceFields.CITY.value] = ""
                    record[RaceFields.STATE.value] = ""
                    record[RaceFields.COUNTRY.value] = tokens[0]
            # By now all the record parts should be available
            if RaceFields.COUNTRY.value in record:
                bib = record[RaceFields.BIB.value]
                self.racers[bib][RaceFields.OVERALL_POSITION.value] = count
                if RaceFields.GENDER.value in record:
                    self.racers[bib][RaceFields.GENDER.value] = record[RaceFields.GENDER.value].strip()
                else:
                    self.racers[bib][RaceFields.GENDER.value] = ""
                if RaceFields.AGE.value in record:
                    self.racers[bib][RaceFields.AGE.value] = record[RaceFields.AGE.value]
                else:
                    self.racers[bib][RaceFields.AGE.value] = ""
                self.racers[bib][RaceFields.CITY.value] = record[RaceFields.CITY.value].strip()
                self.racers[bib][RaceFields.STATE.value] = record[RaceFields.STATE.value].strip()
                self.racers[bib][RaceFields.COUNTRY.value] = record[RaceFields.COUNTRY.value].strip()
                self.racers[bib][RaceFields.BIB.value] = bib
                record = {}

        """
        The following attributes are easier to fill by asking for a particular BIB
        Pace and race time (HH:MM:SS).
            Times are sorted by rank, match these with the rank_to_bib map.
        Race position: Overall, Gender, Division
            Some racers did not identify as Male or Female and their Gender position is missing.
        Some runners also did not went beyond the 20th floor, code handles that.
        """

        if self.debug:
            print("Racers")
            pprint.pprint(self.racers)
            print("Rank to BIB")
            pprint.pprint(self.rank_to_bib)

    def __click__(self, level: int) -> Any:
        button = WebDriverWait(self.driver, 20).until(
            expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, f"div:nth-child({level}) > button")))
        # Bug on Selenium, trigger click with Javascript
        self.driver.execute_script("arguments[0].click();", button)
        sleep(2.5)
        return button


class RacerDetailsScraper:

    def __init__(self, racer: Dict[str, Any], headless: bool = True, load_wait: int = 5, debug_level: int = 0):
        options = Options()
        fp = webdriver.FirefoxProfile()
        service = webdriver.FirefoxService()
        if headless:
            options.add_argument("--headless")
            if debug_level > 1:
                """
                Workaround for: `driver.get_log()` on Firefox
                https://github.com/mozilla/geckodriver/issues/330
                """
                fp.set_preference("devtools.console.stdout.content", "true")
                options.log.LEVEL = "trace"
                service.log_output = subprocess.STDOUT
        options.profile = fp
        self.driver = webdriver.Firefox(
            options=options,
            service=service
        )
        self.load_wait = load_wait
        self.driver.get(racer[RaceFields.URL.value])
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

        Assume racer didn't finish so none of these attributes can be enriched.
        Also, some values can be missing if gender or age was not provided.

        """
        self.racer[RaceFields.TWENTY_FLOOR_POSITION.value] = ""
        self.racer[RaceFields.TWENTY_FLOOR_GENDER_POSITION.value] = ""
        self.racer[RaceFields.TWENTY_FLOOR_DIVISION_POSITION.value] = ""
        self.racer[RaceFields.TWENTY_FLOOR_PACE.value] = ""
        self.racer[RaceFields.TWENTY_FLOOR_TIME.value] = ""
        self.racer[RaceFields.SIXTY_FLOOR_POSITION.value] = ""
        self.racer[RaceFields.SIXTY_FIVE_FLOOR_GENDER_POSITION.value] = ""
        self.racer[RaceFields.SIXTY_FIVE_FLOOR_DIVISION_POSITION.value] = ""
        self.racer[RaceFields.SIXTY_FIVE_FLOOR_PACE.value] = ""
        self.racer[RaceFields.SIXTY_FIVE_FLOOR_TIME.value] = ""
        self.racer[RaceFields.OVERALL_POSITION.value] = ""
        self.racer[RaceFields.GENDER_POSITION.value] = ""
        self.racer[RaceFields.DIVISION_POSITION.value] = ""
        self.racer[RaceFields.PACE.value] = ""
        self.racer[RaceFields.TIME.value] = ""
        self.racer[RaceFields.LEVEL.value] = Level.DNF.value

        # Find the gender and age, influence parsing strategy
        gender = ""
        age = ""
        for div in self.driver.find_elements(By.CSS_SELECTOR, "div[id='ageGender'"):
            value = div.text.strip().split()
            gender = value[0]
            if (RaceFields.GENDER.value in self.racer and self.racer[RaceFields.GENDER.value] == "" and gender != "") or (RaceFields.GENDER.value not in self.racer):
                self.racer[RaceFields.GENDER.value] = gender
            if len(value) > 1:
                age = value[1]
                if (RaceFields.AGE.value in self.racer and self.racer[RaceFields.AGE.value] == "") or (
                        RaceFields.AGE.value not in self.racer and self.racer):
                    self.racer[RaceFields.AGE.value] = age

        for div in self.driver.find_elements(By.CSS_SELECTOR, "div[class='col-7']"):
            value = div.text.strip().split('\n')
            if len(value) == 2:
                self.racer[RaceFields.TIME.value] = value[1]
            if self.debug_level > 0:
                print(value)

        for div in self.driver.find_elements(By.CSS_SELECTOR, "div[class='col-5']"):
            value = div.text.strip().split('\n')
            if len(value) == 2:
                self.racer[RaceFields.PACE.value] = value[1]
            if self.debug_level > 0:
                print(value)

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
                self.racer[RaceFields.TWENTY_FLOOR_POSITION.value] = values[1]
                if gender in ['M', 'F']:
                    self.racer[RaceFields.TWENTY_FLOOR_GENDER_POSITION.value] = values[3]
                if age != "":
                    self.racer[RaceFields.TWENTY_FLOOR_DIVISION_POSITION.value] = values[5]
                self.racer[RaceFields.TWENTY_FLOOR_PACE.value] = values[-3]
                self.racer[RaceFields.TWENTY_FLOOR_TIME.value] = values[-1]
            elif values[0] == '65th Floor' and values[1] != '--':
                self.racer[RaceFields.SIXTY_FLOOR_POSITION.value] = values[1]
                if gender in ['M', 'F']:
                    self.racer[RaceFields.SIXTY_FIVE_FLOOR_GENDER_POSITION.value] = values[3]
                if age != "":
                    self.racer[RaceFields.SIXTY_FIVE_FLOOR_DIVISION_POSITION.value] = values[5]
                self.racer[RaceFields.SIXTY_FIVE_FLOOR_PACE.value] = values[-3]
                self.racer[RaceFields.SIXTY_FIVE_FLOOR_TIME.value] = values[-1]
            elif values[0] == 'Full Course' and values[1] != '--':
                self.racer[RaceFields.LEVEL.value] = Level.FULL.value
                self.racer[RaceFields.OVERALL_POSITION.value] = values[1]
                if gender in ['M', 'F']:
                    self.racer[RaceFields.GENDER_POSITION.value] = values[3]
                if age != "":
                    self.racer[RaceFields.DIVISION_POSITION.value] = values[5]
                self.racer[RaceFields.PACE.value] = values[-3]
                self.racer[RaceFields.TIME.value] = values[-1]
        # Before finishing, pretty format
