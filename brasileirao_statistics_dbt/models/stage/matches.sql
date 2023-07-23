{{ config(materialized='table') }}

with MATCHES as (
  SELECT 
    field_command,
    match_id,
    team
    score,
    (
      SELECT
        team_id
      FROM
        teams_info
      WHERE
        name = REPLACE(unaccent(LOWER(team)), ' ', '-')
    )
  FROM MATCHES_INFO
)

select *
from MATCHES
