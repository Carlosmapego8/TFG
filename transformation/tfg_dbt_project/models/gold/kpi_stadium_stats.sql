select
    f.stadium_id,
    s.stadium_name,
    count(*) as matches_hosted,
    sum(f.total_goals) as total_goals,
    round(avg(f.total_goals::numeric), 2) as avg_goals_per_match,
    sum(case when f.result = 'home_win' then 1 else 0 end) as home_wins,
    sum(case when f.result = 'away_win' then 1 else 0 end) as away_wins,
    sum(case when f.result = 'draw' then 1 else 0 end) as draws
from {{ ref('fct_matches') }} f
inner join {{ ref('dim_stadiums') }} s on s.stadium_id = f.stadium_id
group by f.stadium_id, s.stadium_name
