from dataclasses import dataclass, field
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
from typing import Callable
import numpy as np
from scipy.optimize import linprog

ListKPTeam = list['KPTeam']
ListESPNTeam = list['ESPNTeam']
ListCombinedTeam = list['CombinedTeam']


@dataclass
class KPTeam:
    '''Class containing KenPom data for a specfic team'''
    name: str
    conf: str
    adjEM: float
    adjO: float
    adjO_rk: int
    adjD: float
    adjD_rk: int
    adjT: float
    adjT_rk: int
    oppEM: float
    oppEM_rk: int
    oppO: float
    oppO_rk: int
    oppD: float
    oppD_rk: int
    ncEM: float
    ncEM_rk: int

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
            adjEM = float(cols[4].get_text())
            adjO, adjD, adjT = (float(x.get_text()) for x in cols[5:10:2])
            adjO_rk, adjD_rk, adjT_rk = (int(x.get_text())
                                         for x in cols[6:11:2])
            oppEM, oppO, oppD, ncEM = (float(x.get_text())
                                       for x in cols[13:20:2])
            oppEM_rk, oppO_rk, oppD_rk, ncEM_rk = (int(x.get_text())
                                                   for x in cols[14:21:2])
            teams.append(KPTeam(name, conf, adjEM, adjO, adjO_rk, adjD, adjD_rk,
                         adjT, adjT_rk, oppEM, oppEM_rk, oppO, oppO_rk, oppD, oppD_rk, ncEM, ncEM_rk))

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


@dataclass
class CombinedTeam:
    espn: ESPNTeam
    kp: KPTeam
    misc: dict = field(default_factory=dict)

    @staticmethod
    def combine(espn_teams: ListESPNTeam, kp_teams: ListKPTeam, func: Callable[[ESPNTeam, KPTeam], float]) -> ListCombinedTeam:
        # Matching the KP and ESPN teams is an assignment problem, we need to generate a graph
        # Picking the best match for each ESPN team would probably work fine, but could lead to duplicates. Also this is more fun.
        # https://en.wikipedia.org/wiki/Assignment_problem

        # Make copies of the arguments
        espn_nodes: list[ESPNTeam | None] = espn_teams.copy()
        kp_nodes: list[KPTeam | None] = kp_teams.copy()

        # For the program to work, the same number of nodes are needed on each side
        if len(espn_nodes) > len(kp_nodes):
            kp_nodes.extend([None] * (len(espn_nodes) - len(kp_nodes)))
        elif len(kp_nodes) > len(espn_nodes):
            espn_nodes.extend([None] * (len(kp_nodes) - len(espn_nodes)))

        edges = np.zeros((len(espn_nodes), len(kp_nodes)))

        # Fill the edges with the correct values from the given function
        for r, espn_team in enumerate(espn_nodes):
            for c, kp_team in enumerate(kp_nodes):
                if espn_team is not None and kp_team is not None:
                    edges[r][c] = func(espn_team, kp_team)

        # linprog only does minimization problems
        c = -1 * edges.flatten()

        # Each row of A_eq, b_eq is of the form: sum_i A_ub[row, i] * x[i] = b_eq[row]
        eq_count = len(espn_nodes) + len(kp_nodes)
        A_eq = np.zeros((eq_count, len(c)))
        for i, _ in enumerate(espn_nodes):
            for j, _ in enumerate(kp_nodes):
                A_eq[i][i * len(kp_nodes) + j] = 1
                A_eq[j + len(espn_nodes)][i * len(kp_nodes) + j] = 1
        b_eq = np.ones(eq_count)

        solution = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, 1))

        # No solution
        if not solution.success:
            raise Exception(solution.message)

        # Duplicates
        solution_nd = np.ndarray(shape=edges.shape, buffer=solution.x)
        if np.any(np.sum(solution_nd, 0) != 1) and np.any(np.sum(solution_nd, 1) != 1):
            raise Exception('Duplicates found in solution')

        teams = []
        for i, row in enumerate(solution_nd):
            j, _ = max(enumerate(row), key=lambda x: x[1])
            if i >= len(espn_teams) or j >= len(kp_teams):
                continue
            teams.append(CombinedTeam(espn_teams[i], kp_teams[j]))
        return teams
