with team_names as (
    select home_team as team_name from {{ ref('all_matches') }}
    union
    select away_team from {{ ref('all_matches') }}
),

distinct_teams as (
    select distinct team_name from team_names
),

codes as (
    select team_name, team_code from {{ ref('team_codes') }}
),

teams_with_code as (
    select
        {{ dbt_utils.generate_surrogate_key(['t.team_name']) }} as team_id,
        t.team_name,
        c.team_code
    from distinct_teams t
    left join codes c on c.team_name = t.team_name
),

-- Población media (2021 + 2024) por equipo. Para ENG/SCO/WAL se reparte
-- la población agregada de UK mediante la macro population_share.
population_per_team as (
    select
        twc.team_id,
        round(
            avg(p.population) * max({{ population_share('twc.team_code') }})
        )::bigint as population_avg
    from teams_with_code twc
    left join {{ ref('population') }} p
        on p.country_code = ({{ population_country_code('twc.team_code') }})
    group by twc.team_id
)

select
    twc.team_id,
    twc.team_name,
    twc.team_code,
    pop.population_avg
from teams_with_code twc
left join population_per_team pop using (team_id)
