with home as (
    select
        home_team_id as team_id,
        count(*) as matches_played,
        sum(case when result = 'home_win' then 1 else 0 end) as wins,
        sum(case when result = 'draw' then 1 else 0 end) as draws,
        sum(case when result = 'away_win' then 1 else 0 end) as losses,
        sum(home_goals) as goals_for,
        sum(away_goals) as goals_against
    from {{ ref('fct_matches') }}
    group by home_team_id
),

away as (
    select
        away_team_id as team_id,
        count(*) as matches_played,
        sum(case when result = 'away_win' then 1 else 0 end) as wins,
        sum(case when result = 'draw' then 1 else 0 end) as draws,
        sum(case when result = 'home_win' then 1 else 0 end) as losses,
        sum(away_goals) as goals_for,
        sum(home_goals) as goals_against
    from {{ ref('fct_matches') }}
    group by away_team_id
),

combined as (
    select
        coalesce(h.team_id, a.team_id) as team_id,
        coalesce(h.matches_played, 0) + coalesce(a.matches_played, 0) as matches_played,
        coalesce(h.wins, 0) + coalesce(a.wins, 0) as wins,
        coalesce(h.draws, 0) + coalesce(a.draws, 0) as draws,
        coalesce(h.losses, 0) + coalesce(a.losses, 0) as losses,
        coalesce(h.goals_for, 0) + coalesce(a.goals_for, 0) as goals_for,
        coalesce(h.goals_against, 0) + coalesce(a.goals_against, 0) as goals_against
    from home h
    full outer join away a on h.team_id = a.team_id
)

select
    c.team_id,
    t.team_name,
    t.team_code,
    c.matches_played,
    c.wins,
    c.draws,
    c.losses,
    c.goals_for,
    c.goals_against,
    c.goals_for - c.goals_against as goal_difference,
    c.wins * 3 + c.draws as points,
    round(c.goals_for::numeric / nullif(c.matches_played, 0), 2) as avg_goals_per_match
from combined c
inner join {{ ref('dim_teams') }} t on t.team_id = c.team_id
