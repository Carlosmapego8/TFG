with matches as (
    select *
    from {{ ref('matches') }}
)

select
    match_id,
    tournament_id,
    group_id,
    stadium_id,
    home_team_id,
    away_team_id,
    match_date::date as date_id,
    match_number,
    round_number,
    extract(hour from match_date)::int as match_hour,
    home_goals,
    away_goals,
    home_goals + away_goals as total_goals,
    case
        when home_goals > away_goals then 'home_win'
        when home_goals < away_goals then 'away_win'
        else 'draw'
    end as result,
    data_origin
from matches
