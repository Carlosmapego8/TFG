-- Relación equipo ↔ grupo ↔ torneo derivada de los partidos de fase de grupos.
-- Solo se incluyen filas donde el partido tiene group_name (excluye eliminatorias).

with group_matches as (
    select
        tournament_name,
        tournament_year,
        group_name,
        home_team as team_name
    from {{ ref('all_matches') }}
    where group_name is not null
    union
    select
        tournament_name,
        tournament_year,
        group_name,
        away_team
    from {{ ref('all_matches') }}
    where group_name is not null
),

deduped as (
    select distinct
        tournament_name,
        tournament_year,
        group_name,
        team_name
    from group_matches
)

select
    {{ dbt_utils.generate_surrogate_key(['team_name', 'group_name', 'tournament_year']) }} as team_group_id,
    {{ dbt_utils.generate_surrogate_key(['team_name']) }}                                  as team_id,
    {{ dbt_utils.generate_surrogate_key(['group_name']) }}                                 as group_id,
    {{ dbt_utils.generate_surrogate_key(['tournament_name', 'tournament_year']) }}         as tournament_id
from deduped
