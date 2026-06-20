# TFG dbt project

Pipeline analítico sobre PostgreSQL `eurocup_external` que combina:

- **Bronze**: foreign tables (CSV vía `file_fdw`, Postgres vía `postgres_fdw`) y un volcado directo de MongoDB.
- **Silver**: dimensiones canónicas (`teams`, `groups`, `stadiums`, `tournament`, `re_teams_groups`) y la tabla de hechos `matches`.
- **Gold**: vistas star-schema (`dim_*`, `fct_matches`) y KPIs.

Profile dbt: `tfg_dbt_project` (`~/.dbt/profiles.yml`).

## Comandos

```powershell
# desde transformation/tfg_dbt_project/
& .\venv_dbt_core\Scripts\dbt.exe deps
& .\venv_dbt_core\Scripts\dbt.exe seed
& .\venv_dbt_core\Scripts\dbt.exe build         # run + test
```

## Observabilidad — Elementary

El paquete `elementary-data/elementary` está activo. El hook `on-run-end` que
añade el paquete captura automáticamente cada ejecución de `dbt run/test/build`
en el schema `elementary` de `eurocup_external`.

Para generar el reporte HTML interactivo:

```powershell
# desde transformation/tfg_dbt_project/
& .\venv_dbt_core\Scripts\edr.exe report
```

El reporte queda en `edr_target/elementary_report.html` (ignorado por git).
El profile que usa el CLI es el bloque `elementary:` en `~/.dbt/profiles.yml`.
