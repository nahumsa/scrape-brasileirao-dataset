{% macro team_id_from_team_name() %}
(
    SELECT
        team_id
    FROM
        {{ source('raw', 'teams_info')}}
    WHERE
        name = REPLACE(unaccent(LOWER(team)), ' ', '-')
)
{% endmacro %}
