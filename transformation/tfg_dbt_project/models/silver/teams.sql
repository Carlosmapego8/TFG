with source as (

    select data
    from {{ source('bronze_json', 'euro_groups_json') }}

),

groups as (

    select
        data->>'name' as tournament_name,
        jsonb_array_elements(data->'groups') as group_data
    from source

),

teams as (

    select
        tournament_name,
        group_data->>'name' as group_name,
        jsonb_array_elements(group_data->'teams') as team_data
    from groups

)

select
    {{ dbt_utils.generate_surrogate_key([
        "team_data->>'code'"
    ]) }} as team_id,

    team_data->>'name' as team_name,
    team_data->>'code' as team_code

from teams
group by 1,2,3