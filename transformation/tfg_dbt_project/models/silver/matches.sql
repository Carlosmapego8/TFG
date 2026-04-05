with source as (
    select *
    from {{ source('bronze_csv', 'euro_matches') }}
),

parsed as (
    select
        match_number,
        round_number,
        to_timestamp(
                    regexp_replace(match_date, '[^0-9/: ]', '', 'g'),
                    'DD/MM/YYYY HH24:MI') as match_date,
        location,
        case home_team when 'Türkiye' then 'Turkey'
                       when 'Czechia' then 'Czech Republic'
                       else home_team end as home_team,
        case away_team when 'Türkiye' then 'Turkey'
                       when 'Czechia' then 'Czech Republic'
                       else away_team end as away_team,
        split_part(result, ' - ', 1)::int as home_goals,
        split_part(result, ' - ', 2)::int as away_goals
    from source
),

stadiums as (
    select
        stadium_id,
        stadium_name
    from {{ ref('stadiums') }}
),

teams as (
    select
        team_id,
        team_name
    from {{ ref('teams') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['match_number', 'home_team', 'away_team', 'match_date']) }} as match_id,
    m.match_number,
    m.round_number,
    m.match_date,
    s.stadium_id,
    t_home.team_id as home_team_id,
    t_away.team_id as away_team_id,
    m.home_goals,
    m.away_goals
from parsed m
left join stadiums s on s.stadium_name = m.location
left join teams t_home on t_home.team_name = m.home_team
left join teams t_away on t_away.team_name = m.away_team