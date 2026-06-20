with locations as (
    select distinct location
    from {{ ref('all_matches') }}
    where location is not null
)

select
    {{ dbt_utils.generate_surrogate_key(['location']) }} as stadium_id,
    location as stadium_name
from locations
