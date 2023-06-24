import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

url = "https://www.espn.com.br/futebol/partida/_/jogoId/665923"
response = requests.get(url)
html_content = response.content

soup = BeautifulSoup(html_content, "html.parser")

teams = soup.find_all(
    "h2", class_="ScoreCell__TeamName ScoreCell__TeamName--displayName truncate db"
)

home_team, away_team = [element.text for element in teams]

scores = soup.find_all(
    "div",
    class_="Gamestrip__ScoreContainer flex flex-column items-center justify-center relative",  # noqa
)

home_score, away_score = [element.text for element in scores]


get_numbers_from_string = lambda text: re.findall(r"\d+", text)[0]

home_score, away_score = get_numbers_from_string(home_score), get_numbers_from_string(
    away_score
)

print(home_team, home_score)
print(away_team, away_score)

div_table = soup.find("div", "Table__Scroller")
if div_table:
    table = div_table.find("table")
    data = []
    if table:
        rows = table.find_all("tr")
        for row in rows:
            columns = row.find_all("td")
            if columns:
                row_data = [column.text.strip() for column in columns]
                data.append(row_data)
df = pd.DataFrame(data, columns=["casa", "nome", "fora"])
print(df)
