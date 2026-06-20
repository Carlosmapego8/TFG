{#
  Fracción aproximada de la población del agregado del Banco Mundial que
  corresponde a cada selección. Solo aplica al desglose de Reino Unido
  (Inglaterra/Escocia/Gales sobre GBR). Para el resto de selecciones la
  fracción es 1.0 porque la fila del Banco Mundial ya es del país completo.

  Porcentajes aproximados (estimación ONS 2022):
    - England:  ~85.0%
    - Scotland: ~8.0%
    - Wales:    ~4.5%
    - (Northern Ireland queda el ~2.5% restante, no participa con selección propia aquí)
#}
{% macro population_share(team_code_expr) %}
    case {{ team_code_expr }}
        when 'ENG' then 0.850
        when 'SCO' then 0.080
        when 'WAL' then 0.045
        else 1.0
    end
{% endmacro %}
