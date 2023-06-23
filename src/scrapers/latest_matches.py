import requests
from bs4 import BeautifulSoup


def get_latest_matches_url_set(url: str) -> set[str]:
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")

    links = soup.find_all(
        "a", href=lambda href: href and href.startswith("/futebol/partida/_/jogoId")
    )

    # Extract the href attribute from each link and print them
    all_link_teams = set()

    for link in links:
        all_link_teams.add(link.get("href"))

    return all_link_teams


if __name__ == "__main__":
    team_id = 6154
    BASE_URL = "https://www.espn.com.br"
    LEAGUE_NAME = "bra.1"
    SEASON = 2023
    RESULTS_URL = (
        f"/futebol/time/resultados/_/id/{team_id}/liga/{LEAGUE_NAME}/temporada/{SEASON}"
    )
    results_url = BASE_URL + RESULTS_URL
    all_link_results = get_latest_matches_url_set(results_url)
    print(all_link_results)
