with source as (
    select data
    from {{ source('bronze_json', 'euro_groups_json') }}
),

groups_flat as (
    select
        jsonb_array_elements(data->'groups') as group_data
    from source
)

select
    {{ dbt_utils.generate_surrogate_key(["group_data->>'name'"]) }} as group_id,
    group_data->>'name' as group_name
from groups_flat
group by 1,2