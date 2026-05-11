# Power BI Analysis - PBIP Project

## Descripción

Este directorio contiene el componente de análisis del pipeline. Genera un **proyecto Power BI (PBIP)** que conecta directamente a las vistas de la capa gold de PostgreSQL, proporcionando un modelo semántico completo con relaciones, dimensiones y medidas DAX.

## Formato PBIP

**PBIP (Power BI Project)** es el formato moderno y recomendado por Microsoft para proyectos Power BI:
- ✅ Basado en texto/JSON (git-friendly)
- ✅ Abreable directamente en Power BI Desktop
- ✅ Control de versiones completo
- ✅ Colaboración mejorada
- ✅ Requiere Power BI Desktop 2023.9+ con preview feature habilitada

## Estructura del Proyecto

```
analysis/
├── README.md                                (este archivo)
├── analytics.py                             (clase Analytics para orchestrator)
├── pbip_generator.py                        (generador de proyecto PBIP)
└── euro_analysis/                           (PROYECTO POWER BI)
    ├── euro_analysis.pbip                   (archivo principal del proyecto)
    ├── euro_analysis.SemanticModel/
    │   ├── definition.pbism                 (descriptor del modelo semántico)
    │   └── model.bim                        (modelo Tabular - JSON TOM)
    └── euro_analysis.Report/
        ├── definition.pbir                  (descriptor del report)
        └── report.json                      (layout del report - mínimo)
```

## Contenido del Modelo Semántico

### Tablas de Dimensiones (5)
- **dim_teams**: Equipos participantes
  - Columnas: team_id, team_name, team_code

- **dim_tournaments**: Torneos
  - Columnas: tournament_id, tournament_name, year

- **dim_groups**: Grupos (fases de grupos)
  - Columnas: group_id, group_name

- **dim_stadiums**: Estadios
  - Columnas: stadium_id, stadium_name

- **dim_date**: Fechas (derivadas de los partidos)
  - Columnas: date_id, full_date, year, month, day, weekday

### Tabla de Hechos (1)
- **fct_matches**: Partidos (tabla central)
  - Columnas: match_id, tournament_id, group_id, stadium_id, home_team_id, away_team_id, date_id, match_number, round_number, match_hour, home_goals, away_goals, total_goals, result

### Tablas de KPIs/Agregados (4)
- **kpi_team_stats**: Estadísticas por equipo (home + away combinados)
- **kpi_tournament_summary**: Resumen estadístico global del torneo
- **kpi_stadium_stats**: Estadísticas por estadio
- **kpi_group_standings**: Clasificación de fase de grupos

### Relaciones (Star Schema - 6)
```
fct_matches.tournament_id  → dim_tournaments.tournament_id
fct_matches.group_id       → dim_groups.group_id
fct_matches.stadium_id     → dim_stadiums.stadium_id
fct_matches.home_team_id   → dim_teams.team_id (activa)
fct_matches.away_team_id   → dim_teams.team_id (inactiva - cross-filtering both directions)
fct_matches.date_id        → dim_date.date_id
```

### Medidas DAX (9)
Las siguientes medidas están predefinidas en la tabla `fct_matches`:

1. **Total Partidos** = `COUNTROWS(fct_matches)`
2. **Total Goles** = `SUM(fct_matches[total_goals])`
3. **Media Goles/Partido** = `AVERAGE(fct_matches[total_goals])`
4. **Victorias Local** = `CALCULATE(COUNTROWS(fct_matches), fct_matches[result]="home_win")`
5. **Victorias Visitante** = `CALCULATE(COUNTROWS(fct_matches), fct_matches[result]="away_win")`
6. **Empates** = `CALCULATE(COUNTROWS(fct_matches), fct_matches[result]="draw")`
7. **% Victoria Local** = `DIVIDE([Victorias Local], [Total Partidos], 0)`
8. **% Victoria Visitante** = `DIVIDE([Victorias Visitante], [Total Partidos], 0)`
9. **% Empate** = `DIVIDE([Empates], [Total Partidos], 0)`

## Cómo Usar

### Requisitos Previos
1. **Power BI Desktop** (2023.9 o superior)
2. **PostgreSQL ODBC Driver** instalado en tu máquina
   - Descargar desde: https://www.postgresql.org/download/windows/
   - Asegurate de instalar el driver ODBC
3. Credenciales de acceso a PostgreSQL (servidor, base de datos, usuario, contraseña)

### Pasos para Abrir el Proyecto

1. **Habilitar PBIP en Power BI Desktop**:
   - Abre Power BI Desktop
   - Vete a: `File` → `Options and settings` → `Options`
   - Busca: `Preview features`
   - Habilita: `Power BI projects`
   - Reinicia Power BI Desktop

2. **Abrir el Proyecto**:
   - En Power BI Desktop: `File` → `Open` → `Browse`
   - Navega a: `analysis/euro_analysis/euro_analysis.pbip`
   - Abre el archivo

3. **Configurar la Conexión PostgreSQL**:
   - En Power BI, verás un cuadro de diálogo de credenciales
   - Completa los detalles de conexión:
     - **Server**: Tu servidor PostgreSQL (ej: localhost)
     - **Database**: Nombre de tu base de datos (ej: tfg_warehouse)
     - **Username**: Tu usuario PostgreSQL
     - **Password**: Tu contraseña
   - Haz clic en "Connect"

4. **Actualizar Datos**:
   - Una vez conectado, Power BI cargará los datos de las vistas gold
   - Puedes crear dashboards y reportes usando las tablas, relaciones y medidas

## Regenerar el Proyecto PBIP

Si cambias las tablas gold o necesitas actualizar el modelo:

```bash
cd analysis
python pbip_generator.py
```

O desde Python:

```python
from pbip_generator import generate_pbip_project
from config_loader import load_config

db_config = load_config("../ingestion/db_config.py", "DB_CONFIG")
generate_pbip_project(db_config, output_dir=".")
```

## Próximos Pasos

### Dentro del Pipeline (Ingestion)
El componente Analytics será integrado en el pipeline de ingesta:

```yaml
# pipeline_config.yml
analytics:
  type: "pbip"
  db_config: "db_config.py"
  output_dir: "analysis"
```

En `main.py`, se instanciará y ejecutará automáticamente:

```python
from analysis.analytics import Analytics

analytics = Analytics(
    db_config_path=config["database"]["config_file"],
    output_dir="analysis"
)
orchestrator.set_analytics(analytics)
```

### En Power BI Desktop
Una vez el proyecto esté abierto:
1. Explora el modelo en la vista de diagrama (verás las relaciones)
2. Crea visualizaciones usando las tablas (las medidas DAX están listas para usar)
3. Construye dashboards para análisis:
   - Rendimiento de equipos (kpi_team_stats)
   - Estadísticas de torneos (kpi_tournament_summary)
   - Análisis por estadio (kpi_stadium_stats)
   - Tablas de clasificación (kpi_group_standings)
4. Publica a Power BI Service para compartir reportes

## Troubleshooting

**Problema**: "No se puede abrir el archivo .pbip"
- **Solución**: Asegúrate de haber habilitado PBIP en Preview Features y reiniciado Power BI

**Problema**: "Error de conexión PostgreSQL"
- **Solución**: Verifica que:
  1. PostgreSQL ODBC driver está instalado
  2. Las credenciales son correctas
  3. El servidor es accesible desde tu máquina
  4. El esquema `gold` existe en la base de datos

**Problema**: "Las tablas no cargan datos"
- **Solución**: Asegúrate de que:
  1. El pipeline dbt ha completado exitosamente (vistas gold existen)
  2. Hay datos en las vistas gold (ejecuta `dbt test` para verificar)
  3. El usuario PostgreSQL tiene permisos SELECT en el esquema gold

## Archivos de Configuración

- `pbip_generator.py`: Script que genera los archivos del proyecto PBIP a partir de un modelo TOM
- `analytics.py`: Clase Analytics que se integra con el Orchestrator

Ambos archivos se pueden reutilizar y regenerar el proyecto PBIP cuando sea necesario.

## Notas Técnicas

- El proyecto PBIP usa **Power Query M** para consultar directamente las vistas gold en PostgreSQL
- Las relaciones usan el patrón **star schema** para optimizar análisis
- La relación `home_team` está activa (por defecto) y la relación `away_team` está inactiva (para evitar ambigüedad en filtros)
- Los datos se cargan en modo **Import** (copia local en Power BI) para mejor rendimiento
- Se pueden cambiar a **DirectQuery** si prefieres tiempo real

---

**Última actualización**: 2026-05-11
**Proyecto**: Euro 2024 Football Tournament Analytics (TFG)
