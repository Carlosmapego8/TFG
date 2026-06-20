with bronze as (
    select * from {{ ref('all_matches') }}
),

stadiums as (
    select stadium_id, stadium_name from {{ ref('stadiums') }}
),

teams as (
    select team_id, team_name from {{ ref('teams') }}
),

tournament as (
    select tournament_id, tournament_name, year as tournament_year from {{ ref('tournament') }}
),

team_groups as (
    select team_id, group_id, tournament_id from {{ ref('re_teams_groups') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['m.tournament_year', 'm.match_number', 'm.home_team', 'm.away_team', 'm.match_date']) }} as match_id,
    m.match_number,
    m.round_number,
    m.match_date,
    s.stadium_id,
    t_home.team_id as home_team_id,
    t_away.team_id as away_team_id,
    tn.tournament_id,
    tg.group_id,
    m.home_goals,
    m.away_goals
from bronze m
left join tournament  tn      on tn.tournament_name = m.tournament_name
                              and tn.tournament_year = m.tournament_year
left join stadiums    s       on s.stadium_name = m.location
left join teams       t_home  on t_home.team_name = m.home_team
left join teams       t_away  on t_away.team_name = m.away_team
left join team_groups tg      on tg.team_id = t_home.team_id
                              and tg.tournament_id = tn.tournament_id
