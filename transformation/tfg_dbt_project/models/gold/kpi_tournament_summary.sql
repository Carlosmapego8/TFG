select
    tournament_id,
    count(*) as total_matches,
    sum(total_goals) as total_goals,
    round(avg(total_goals::numeric), 2) as avg_goals_per_match,
    max(total_goals) as max_goals_in_match,
    sum(case when result = 'home_win' then 1 else 0 end) as total_home_wins,
    sum(case when result = 'away_win' then 1 else 0 end) as total_away_wins,
    sum(case when result = 'draw' then 1 else 0 end) as total_draws,
    round(100.0 * sum(case when result = 'home_win' then 1 else 0 end) / count(*), 1) as home_win_pct,
    round(100.0 * sum(case when result = 'away_win' then 1 else 0 end) / count(*), 1) as away_win_pct,
    round(100.0 * sum(case when result = 'draw' then 1 else 0 end) / count(*), 1) as draw_pct
from {{ ref('fct_matches') }}
group by tournament_id
