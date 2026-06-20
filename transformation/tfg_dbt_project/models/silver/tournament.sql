with tournaments as (
    select distinct
        tournament_name,
        tournament_year
    from {{ ref('all_matches') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['tournament_name', 'tournament_year']) }} as tournament_id,
    tournament_name,
    tournament_year as year
from tournaments
