with source as (
    select data
    from {{ source('bronze_json', 'euro_groups_json') }}
),

tournaments_flat as (
    select
        data->>'name' as tournament_name,
        (data->>'year')::int as tournament_year,
        jsonb_array_elements(data->'groups') as group_data
    from source
),

teams_flat as (
    select
        tournament_name,
        tournament_year,
        group_data->>'name' as group_name,
        jsonb_array_elements(group_data->'teams') as team_data
    from tournaments_flat
)

select
    {{ dbt_utils.generate_surrogate_key(["team_data->>'code'", "group_name", "tournament_year"]) }} as team_group_id,
    {{ dbt_utils.generate_surrogate_key(["team_data->>'code'"]) }} as team_id,
    {{ dbt_utils.generate_surrogate_key(["group_name"]) }} as group_id,
    {{ dbt_utils.generate_surrogate_key(["tournament_name", "tournament_year"]) }} as tournament_id
from teams_flat