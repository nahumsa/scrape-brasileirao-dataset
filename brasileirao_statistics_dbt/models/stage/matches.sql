{{ config(materialized='table') }}

with MATCHES as (
  SELECT 
    match_id,
    field_command,
    score,
    (
      SELECT
        team_id
      FROM
        {{ source('raw', 'teams_info')}}
      WHERE
        name = REPLACE(unaccent(LOWER(team)), ' ', '-')
    )
  FROM {{ source('raw', 'matches_info')}}
)
select *
from MATCHES
