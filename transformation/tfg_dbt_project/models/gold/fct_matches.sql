with matches as (
    select *
    from {{ ref('matches') }}
)

select
    match_id,
    --tournament_id,
    --group_id,
    stadium_id,
    home_team_id,
    away_team_id,
    match_date::date as date_id,
    match_number,
    round_number,
    home_goals,
    away_goals
from matches 