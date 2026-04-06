select
    team_id,
    team_name,
    team_code
from {{ ref('teams') }}