select
    team_id,
    team_name,
    team_code,
    population_avg
from {{ ref('teams') }}
