WITH statistics AS (
    SELECT 
        match_id,
        {{ team_id_from_team_name() }} as team_id,
        stat_name,
        stat_value
    FROM {{ source('raw', 'matches_statistics')}}
)

SELECT *
FROM statistics