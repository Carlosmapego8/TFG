select
    stadium_id,
    stadium_name
from {{ ref('stadiums') }}