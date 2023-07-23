# Scraper para dados do Brasileirão

Esse repositório retira os dados do site `https://espn.com.br` referentes a partidas de futebol jogadas durante o Campeonato Brasileiro Série A (Brasileirão).


# Tecnologias utilizadas
- [Python 3.10](https://www.python.org/)
- [Dagster](https://dagster.io/)
- [PostgreSQL](https://www.postgresql.org/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

# Database
Vamos utilizar uma database PostGRESQL para guardar os dados que vão ser retirados do site da forma bruta (raw). Após o armazenamento utilizaremos [DBT](https://www.getdbt.com/) para normalizá-los e fazer cálculos para cada data mart.

## Raw
```mermaid
erDiagram
    TEAMS_INFO ||--o{ TEAMS_MATCHES : has
    TEAMS_MATCHES ||--|{ MATCH_STATS : has
    TEAMS_MATCHES ||--|{ MATCH_INFO : has
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
    MATCH_INFO {
        int id
        int match_id[fk]
        string team
        string field_command
        int score
    }
    MATCH_STATS {
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
