# Scraper para dados do Brasileirão

Esse repositório retira os dados do site `https://espn.com.br` referentes a partidas de futebol jogadas durante o Campeonato Brasileiro Série A (Brasileirão).


# Tecnologias utilizadas

- [Python 3.10](https://www.python.org/)
- [Dagster](https://dagster.io/)
- [PostgreSQL](https://www.postgresql.org/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [DBT](https://www.getdbt.com/)

# Arquitetura

Como estamos trabalhando com um trabalho em lote (batch) a arquitetura é pensada para suprir a necessidade de atualizar os dados em períodos que são maiores do que segundos (nesse caso, a cada dia). Portanto, escolhi utilizar Dagster para orquestrar o webscraping e as transformações que estão implementadas utilizando o DBT, tendo a seguinte arquitetura:

```mermaid
flowchart LR
    subgraph Dagster
    id1[webpage]  -->|scraping| id2[(raw_data)]
    id2 -->|DBT| id3[(staging)]
    id3 -->|DBT| id4[(data mart)]
    id3 -->|DBT| id5[(data mart)]
    id3 -->|DBT| id6[(data mart)]
    id3 -->|DBT| id7[(data mart)]
    end
    id4 -.-> id8(superset)
    id5 -.-> id8
    id6 -.-> id8
    id7 -.-> id8
```

# Database

Vamos utilizar uma database [PostgreSQL](https://www.postgresql.org/) para guardar os dados que vão ser retirados do site da forma bruta (raw). Após o armazenamento utilizaremos [DBT](https://www.getdbt.com/) para normalizá-los, guardar em um schema de staging e fazer cálculos para cada data mart.

## Raw

```mermaid
erDiagram
    TEAMS_INFO ||--o{ TEAMS_MATCHES : has
    TEAMS_MATCHES ||--|{ MATCHES_STATS : has
    TEAMS_MATCHES ||--|{ MATCHES_INFO : has
    TEAMS_INFO {
        bigint id
        bigint team_id[fk]
        string name
    }
    TEAMS_MATCHES {
        int id
        string url
        int match_id[fk]
        int team_id[fk]
    }
    MATCHES_INFO {
        int id
        int match_id[fk]
        string team
        string field_command
        int score
    }
    MATCHES_STATS {
        int id
        int match_id[fk]
        string team
        string stat_name
        float stat_value
    }
```

## Normalizada

```mermaid
erDiagram
    TEAMS ||--o{ MATCHES : has
    MATCHES ||--|{ MATCH_STATS : has
    MATCHES ||--|{ CHAMPIONSHIP : has

    TEAMS {
        bigint id
        string name
    }
    CHAMPIONSHIP {
        int id
        string name
    }
    MATCHES {
        int id
        int home_team_id
        int away_team_id
        int championship_id
        int home_team_score
        int away_team_score
    }
    MATCH_STATS {
        int id
        int match_id[fk]
        int team_id[fk]
        string stat_name
        float stat_value
    }
```

## Dagster

![dagster dag](./images/brasileirao-scraping-dagster.png)
