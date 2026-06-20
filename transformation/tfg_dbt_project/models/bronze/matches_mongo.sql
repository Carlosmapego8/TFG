-- Bronze: Mongo eurocup → filtra solo Euro 2024, desanida matches[] y conforma esquema unificado.

with eurocup as (
    select
        name                  as tournament_name,
        matches::jsonb        as matches_arr
    from {{ source('bronze_mongo', 'eurocup') }}
    where name = 'Euro 2024'
),

unnested as (
    select
        e.tournament_name,
        m.match_data,
        m.idx
    from eurocup e,
         lateral jsonb_array_elements(e.matches_arr) with ordinality as m(match_data, idx)
)

select
    tournament_name,
    (regexp_match(tournament_name, '\d{4}'))[1]::int                                  as tournament_year,
    idx::int                                                                          as match_number,
    match_data->>'round'                                                              as round_number,
    (
        (match_data->>'date')::date + (match_data->>'time')::time
    )::timestamp                                                                      as match_date,
    match_data->>'ground'                                                             as location,
    match_data->>'team1'                                                              as home_team,
    match_data->>'team2'                                                              as away_team,
    case
        when match_data->>'group' like 'Group %' then match_data->>'group'
        else null
    end                                                                               as group_name,
    (match_data->'score'->'ft'->>0)::int                                              as home_goals,
    (match_data->'score'->'ft'->>1)::int                                              as away_goals
from unnested
