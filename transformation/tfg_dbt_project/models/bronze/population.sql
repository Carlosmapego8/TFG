-- Bronze: población filtrada a los años de los torneos (2021 y 2024) y con tipos casteados.

select
    "Country Name"::text   as country_name,
    "Country Code"::text   as country_code,
    "Year"::int            as year,
    "Value"::bigint        as population
from {{ source('bronze_csv', 'population') }}
where "Year" in ('2021', '2024')
  and "Value" is not null
  and "Value" <> ''
