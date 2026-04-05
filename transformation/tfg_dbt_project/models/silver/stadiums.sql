with source as (
    select distinct location
    from {{ source('bronze_csv', 'euro_matches') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['location']) }} as stadium_id,
    location as stadium_name
from source