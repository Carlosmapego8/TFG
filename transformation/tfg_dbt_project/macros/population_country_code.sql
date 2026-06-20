{#
  Mapea el team_code (convención UEFA) al Country Code que usa la fuente de
  población (ISO-3, Banco Mundial). Hay dos tipos de discrepancia:

  1. UEFA vs ISO-3 para varios países (UEFA usa siglas comunes en fútbol,
     el Banco Mundial usa ISO-3 oficial):
       GER → DEU, NED → NLD, POR → PRT, SUI → CHE, CRO → HRV, DEN → DNK.

  2. Reino Unido no se desglosa: ENG, SCO, WAL → GBR (la fracción de
     población se ajusta en population_share).

  Para el resto de selecciones el team_code coincide con el ISO-3.
#}
{% macro population_country_code(team_code_expr) %}
    case {{ team_code_expr }}
        when 'ENG' then 'GBR'
        when 'SCO' then 'GBR'
        when 'WAL' then 'GBR'
        when 'GER' then 'DEU'
        when 'NED' then 'NLD'
        when 'POR' then 'PRT'
        when 'SUI' then 'CHE'
        when 'CRO' then 'HRV'
        when 'DEN' then 'DNK'
        else {{ team_code_expr }}
    end
{% endmacro %}
