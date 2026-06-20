with grp as (
    select distinct group_name
    from {{ ref('all_matches') }}
    where group_name is not null
)

select
    {{ dbt_utils.generate_surrogate_key(['group_name']) }} as group_id,
    group_name
from grp
