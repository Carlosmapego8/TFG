select
    group_id,
    group_name
from {{ ref('groups') }}