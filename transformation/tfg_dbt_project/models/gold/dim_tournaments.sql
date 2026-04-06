select
    tournament_id,
    tournament_name,
    year
from {{ ref('tournament') }}