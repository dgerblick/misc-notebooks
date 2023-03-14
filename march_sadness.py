from dataclasses import dataclass
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

ListKPTeam = list['KPTeam']
ListESPNTeam = list['ESPNTeam']


@dataclass
class KPTeam:
    '''Class containing KenPom data for a specfic team'''
    name: str
    conf: str
    adj_o: float
    adj_d: float
    adj_t: float

    @staticmethod
    def list_all(driver: WebDriver) -> ListKPTeam:
        # Navigate to the website
        driver.get('https://kenpom.com')

        # Wait for table to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'ratings-table')))

        # Extract the HTML after the element is loaded and use BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        teams = []

        # Find Rating table
        table = soup.find('table', id='ratings-table')
        if not table:
            return []

        # Process all rows
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) != 21:
                continue
            name = cols[1].find('a').get_text()
            conf = cols[2].get_text()
            adj_o = cols[5].get_text()
            adj_d = cols[7].get_text()
            adj_t = cols[9].get_text()
            teams.append(KPTeam(name, conf, adj_o, adj_d, adj_t))

        return teams


@dataclass
class ESPNTeam:
    id: str
    uid: str
    slug: str
    abbreviation: str
    displayName: str
    shortDisplayName: str
    name: str
    nickname: str
    location: str
    color: str
    isActive: str
    isAllStar: str
    logos: list
    links: list
    alternateColor: str = None

    @staticmethod
    def list_all() -> ListESPNTeam:
        teams = []

        page = 1
        while True:
            # Load page of ESPN API results and process into object
            response = requests.get(
                f'https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams?page={page}')
            data = response.json()['sports'][0]['leagues'][0]['teams']
            if len(data) > 0:
                teams.extend(ESPNTeam(**x['team']) for x in data)
                page += 1
            else:
                break
        return teams
