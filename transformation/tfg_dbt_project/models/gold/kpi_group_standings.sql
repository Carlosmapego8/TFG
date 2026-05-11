with group_matches as (
    select *
    from {{ ref('fct_matches') }}
    where group_id is not null
),

home_stats as (
    select
        group_id,
        home_team_id as team_id,
        count(*) as matches_played,
        sum(case when result = 'home_win' then 1 else 0 end) as wins,
        sum(case when result = 'draw' then 1 else 0 end) as draws,
        sum(case when result = 'away_win' then 1 else 0 end) as losses,
        sum(home_goals) as goals_for,
        sum(away_goals) as goals_against
    from group_matches
    group by group_id, home_team_id
),

away_stats as (
    select
        group_id,
        away_team_id as team_id,
        count(*) as matches_played,
        sum(case when result = 'away_win' then 1 else 0 end) as wins,
        sum(case when result = 'draw' then 1 else 0 end) as draws,
        sum(case when result = 'home_win' then 1 else 0 end) as losses,
        sum(away_goals) as goals_for,
        sum(home_goals) as goals_against
    from group_matches
    group by group_id, away_team_id
),

combined as (
    select
        coalesce(h.group_id, a.group_id) as group_id,
        coalesce(h.team_id, a.team_id) as team_id,
        coalesce(h.matches_played, 0) + coalesce(a.matches_played, 0) as matches_played,
        coalesce(h.wins, 0) + coalesce(a.wins, 0) as wins,
        coalesce(h.draws, 0) + coalesce(a.draws, 0) as draws,
        coalesce(h.losses, 0) + coalesce(a.losses, 0) as losses,
        coalesce(h.goals_for, 0) + coalesce(a.goals_for, 0) as goals_for,
        coalesce(h.goals_against, 0) + coalesce(a.goals_against, 0) as goals_against
    from home_stats h
    full outer join away_stats a
        on h.group_id = a.group_id and h.team_id = a.team_id
)

select
    g.group_name,
    t.team_name,
    t.team_code,
    c.matches_played,
    c.wins,
    c.draws,
    c.losses,
    c.goals_for,
    c.goals_against,
    c.goals_for - c.goals_against as goal_difference,
    c.wins * 3 + c.draws as points
from combined c
inner join {{ ref('dim_teams') }} t on t.team_id = c.team_id
inner join {{ ref('dim_groups') }} g on g.group_id = c.group_id
order by g.group_name, c.wins * 3 + c.draws desc, c.goals_for - c.goals_against desc, c.goals_for desc
