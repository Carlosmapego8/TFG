with dates as (
    select distinct match_date::date as date_id
    from {{ ref('matches') }}
)

select
    date_id,
    date_id as full_date,
    extract(year from date_id)::int as year,
    extract(month from date_id)::int as month,
    extract(day from date_id)::int as day,
    trim(to_char(date_id, 'Day')) as weekday
from dates
