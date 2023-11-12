from selenium import webdriver
from selenium.webdriver.firefox.options import Options

EMPIRE_STATE_2013_RACE_RESULTS = "https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Results"


class EmpireStateScrapper:

    def __init__(self, headless: bool = True):
        options = Options()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def scrape(self) -> str:
        self.driver.get(EMPIRE_STATE_2013_RACE_RESULTS)
        return self.driver.page_source
