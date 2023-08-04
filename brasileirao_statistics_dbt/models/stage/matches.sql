{{ config(materialized='table') }}

with MATCHES as (
  SELECT 
    match_id,
    field_command,
    score,
    {{ team_id_from_team_name() }} as team_id
  FROM {{ source('raw', 'matches_info')}}
)
select *
from MATCHES
