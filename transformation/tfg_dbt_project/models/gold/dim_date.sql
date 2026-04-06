with dates as (
    select distinct match_date
    from {{ ref('matches') }}
)

select
    match_date::date as date_id,
    extract(year from match_date) as year,
    extract(month from match_date) as month,
    extract(day from match_date) as day,
    to_char(match_date, 'Day') as weekday,
    extract(hour from match_date) as hour
from dates