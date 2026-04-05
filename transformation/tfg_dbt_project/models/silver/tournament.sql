with source as (
    select data
    from {{ source('bronze_json', 'euro_groups_json') }}
)

select
    {{ dbt_utils.generate_surrogate_key(["data->>'name'"]) }} as tournament_id,
    data->>'name' as tournament_name,
    (data->>'year')::int as year
from source