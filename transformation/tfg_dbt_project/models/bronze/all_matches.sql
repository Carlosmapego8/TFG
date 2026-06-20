-- Bronze: unión de los matches conformados desde CSV (2021) y Mongo (2024).
-- Consumido por todos los silver para evitar duplicar el union.

select * from {{ ref('matches_csv') }}
union all
select * from {{ ref('matches_mongo') }}
