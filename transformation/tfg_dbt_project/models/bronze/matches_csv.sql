-- Bronze: matches CSV foreign table → filtra solo Euro 2021 y conforma esquema unificado.

with source as (
    select *
    from {{ source('bronze_csv', 'euro_matches_raw') }}
    where match_date like '%/2021 %'
)

select
    'Euro 2021'::text                                                                 as tournament_name,
    2021::int                                                                         as tournament_year,
    match_number::int                                                                 as match_number,
    case round_number
        when '1' then 'Matchday 1'
        when '2' then 'Matchday 2'
        when '3' then 'Matchday 3'
        else round_number
    end                                                                               as round_number,
    to_timestamp(regexp_replace(match_date, '[^0-9/: ]', '', 'g'), 'DD/MM/YYYY HH24:MI') as match_date,
    location                                                                          as location,
    case home_team
        when 'Türkiye' then 'Turkey'
        when 'Czechia' then 'Czech Republic'
        else home_team
    end                                                                               as home_team,
    case away_team
        when 'Türkiye' then 'Turkey'
        when 'Czechia' then 'Czech Republic'
        else away_team
    end                                                                               as away_team,
    case
        when group_name like 'Group %' then group_name
        else null
    end                                                                               as group_name,
    nullif(split_part(result, ' - ', 1), '')::int                                     as home_goals,
    nullif(split_part(result, ' - ', 2), '')::int                                     as away_goals
from source
