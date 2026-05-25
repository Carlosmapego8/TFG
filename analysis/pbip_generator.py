"""
PBIP Generator - Generates Power BI Project (PBIP) with TOM model
Connects to PostgreSQL gold schema and creates a star schema model with DAX measures
"""

import json
import os
from pathlib import Path
from datetime import datetime


def generate_pbip_project(db_config: dict, output_dir: str = ".", project_name: str = "euro_analysis"):
    """
    Generates a complete PBIP (Power BI Project) structure with:
    - TOM model (model.bim) pointing to PostgreSQL gold views
    - PBIP project files
    - Relationships and DAX measures

    Args:
        db_config: Dictionary with PostgreSQL connection details
                  {host, dbname, user, password, port}
        output_dir: Directory where PBIP files will be created
        project_name: Name of the Power BI project (default: euro_analysis)
    """
    project_dir = Path(output_dir) / project_name
    pbip_path = project_dir / f"{project_name}.pbip"

    # If structure already exists, skip generation to preserve manual changes
    if pbip_path.exists():
        print(f"[SKIP] PBIP project already exists at: {project_dir}")
        print(f"       Skipping generation to preserve manual changes.")
        return str(project_dir)

    # Create directory structure
    semantic_model_dir = project_dir / f"{project_name}.SemanticModel"
    report_dir = project_dir / f"{project_name}.Report"

    semantic_model_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    # Generate model.bim (TOM JSON)
    tom_model = generate_tom_model(db_config)

    # Write model.bim
    model_bim_path = semantic_model_dir / "model.bim"
    with open(model_bim_path, "w", encoding="utf-8") as f:
        json.dump(tom_model, f, indent=2, ensure_ascii=False)

    # Write definition.pbism (semantic model pointer)
    definition_pbism = {
        "version": "4.0"
    }
    definition_pbism_path = semantic_model_dir / "definition.pbism"
    with open(definition_pbism_path, "w", encoding="utf-8") as f:
        json.dump(definition_pbism, f, indent=2)

    # Write definition.pbir (report pointer)
    definition_pbir = {
        "version": "4.0",
        "datasetReference": {
            "byPath": {
                "path": f"../{project_name}.SemanticModel"
            }
        }
    }
    definition_pbir_path = report_dir / "definition.pbir"
    with open(definition_pbir_path, "w", encoding="utf-8") as f:
        json.dump(definition_pbir, f, indent=2)

    # Write report.json (minimal report layout)
    report_json = generate_report_json()
    report_json_path = report_dir / "report.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_json, f, indent=2)

    # Write main .pbip file
    pbip_content = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": f"{project_name}.Report"
                }
            }
        ]
    }
    pbip_path = project_dir / f"{project_name}.pbip"
    with open(pbip_path, "w", encoding="utf-8") as f:
        json.dump(pbip_content, f, indent=2)

    print(f"[OK] PBIP project generated at: {project_dir}")
    print(f"   - Model: {model_bim_path}")
    print(f"   - Report: {report_json_path}")
    return str(project_dir)


def generate_tom_model(db_config: dict) -> dict:
    """Generates the Tabular Object Model (TOM) JSON structure"""

    # PostgreSQL connection string for ODBC
    server = db_config.get("host", "localhost")
    dbname = db_config.get("dbname", "tfg_warehouse")
    user = db_config.get("user", "postgres")
    password = db_config.get("password", "")
    port = db_config.get("port", 5432)

    # ODBC connection string
    odbc_connection = (
        f"Driver={{PostgreSQL Unicode}};Server={server};Port={port};"
        f"Database={dbname};UID={user};PWD={password};"
    )

    tom_model = {
        "compatibilityLevel": 1550,
        "model": {
            "name": "euro_analysis",
            "description": "Euro 2024 Analysis - Football Tournament Analytics",
            "culture": "es-ES",
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "es-ES",
            "tables": generate_tables(odbc_connection),
            "relationships": generate_relationships()
        }
    }

    return tom_model


def generate_tables(odbc_connection: str) -> list:
    """Generates all 10 tables with Power Query M expressions"""

    tables = []

    # Dimension tables
    dim_definitions = [
        {
            "name": "dim_teams",
            "description": "Dimensión de equipos participantes",
            "sql_table": "dim_teams",
            "columns": ["team_id", "team_name", "team_code"]
        },
        {
            "name": "dim_tournaments",
            "description": "Dimensión de torneos",
            "sql_table": "dim_tournaments",
            "columns": ["tournament_id", "tournament_name", "year"]
        },
        {
            "name": "dim_groups",
            "description": "Dimensión de grupos",
            "sql_table": "dim_groups",
            "columns": ["group_id", "group_name"]
        },
        {
            "name": "dim_stadiums",
            "description": "Dimensión de estadios",
            "sql_table": "dim_stadiums",
            "columns": ["stadium_id", "stadium_name"]
        },
        {
            "name": "dim_date",
            "description": "Dimensión de fechas",
            "sql_table": "dim_date",
            "columns": ["date_id", "full_date", "year", "month", "day", "weekday"]
        }
    ]

    for dim_def in dim_definitions:
        tables.append(
            generate_table_definition(
                dim_def["name"],
                dim_def["description"],
                dim_def["sql_table"],
                dim_def["columns"],
                odbc_connection
            )
        )

    # Fact table
    tables.append(
        generate_table_definition(
            "fct_matches",
            "Tabla de hechos - Partidos con métricas",
            "fct_matches",
            ["match_id", "tournament_id", "group_id", "stadium_id",
             "home_team_id", "away_team_id", "date_id", "match_number",
             "round_number", "match_hour", "home_goals", "away_goals",
             "total_goals", "result"],
            odbc_connection,
            include_measures=True
        )
    )

    # KPI tables
    kpi_definitions = [
        {
            "name": "kpi_team_stats",
            "description": "Estadísticas agregadas por equipo",
            "sql_table": "kpi_team_stats",
            "columns": ["team_id", "team_name", "team_code", "matches_played",
                       "wins", "draws", "losses", "goals_for", "goals_against",
                       "goal_difference", "points", "avg_goals_per_match"]
        },
        {
            "name": "kpi_tournament_summary",
            "description": "Resumen estadístico global del torneo",
            "sql_table": "kpi_tournament_summary",
            "columns": ["tournament_id", "total_matches", "total_goals",
                       "avg_goals_per_match", "max_goals_in_match",
                       "total_home_wins", "total_away_wins", "total_draws",
                       "home_win_pct", "away_win_pct", "draw_pct"]
        },
        {
            "name": "kpi_stadium_stats",
            "description": "Estadísticas por estadio",
            "sql_table": "kpi_stadium_stats",
            "columns": ["stadium_id", "stadium_name", "matches_hosted",
                       "total_goals", "avg_goals_per_match", "home_wins",
                       "away_wins", "draws"]
        },
        {
            "name": "kpi_group_standings",
            "description": "Clasificación de la fase de grupos",
            "sql_table": "kpi_group_standings",
            "columns": ["group_name", "team_name", "team_code", "matches_played",
                       "wins", "draws", "losses", "goals_for", "goals_against",
                       "goal_difference", "points"]
        }
    ]

    for kpi_def in kpi_definitions:
        tables.append(
            generate_table_definition(
                kpi_def["name"],
                kpi_def["description"],
                kpi_def["sql_table"],
                kpi_def["columns"],
                odbc_connection
            )
        )

    return tables


def generate_table_definition(
    table_name: str,
    description: str,
    sql_table: str,
    columns: list,
    odbc_connection: str,
    include_measures: bool = False
) -> dict:
    """Generates a single table definition with columns and optional measures"""

    # Power Query M expression - simple SELECT from PostgreSQL gold view
    m_expression = (
        f'let\n'
        f'    Source = Odbc.Database("{odbc_connection}"),\n'
        f'    gold_Schema = Source{{{{"Schema"="gold"}}}}[Data],\n'
        f'    {sql_table}_Table = gold_Schema{{{{{{"Name"="{sql_table}"}}}}}}[Data]\n'
        f'in\n'
        f'    {sql_table}_Table'
    )

    table_def = {
        "name": table_name,
        "description": description,
        "partitions": [
            {
                "name": f"Partition",
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": m_expression
                }
            }
        ],
        "columns": [
            {
                "name": col,
                "dataType": "string"
            }
            for col in columns
        ]
    }

    # Add measures to fct_matches
    if include_measures:
        table_def["measures"] = generate_dax_measures()

    return table_def


def generate_dax_measures() -> list:
    """Generates DAX measures for the fact table"""

    measures = [
        {
            "name": "Total Partidos",
            "expression": "COUNTROWS(fct_matches)",
            "formatString": "#,0"
        },
        {
            "name": "Total Goles",
            "expression": "SUM(fct_matches[total_goals])",
            "formatString": "#,0"
        },
        {
            "name": "Media Goles/Partido",
            "expression": "AVERAGE(fct_matches[total_goals])",
            "formatString": "0.00"
        },
        {
            "name": "Victorias Local",
            "expression": 'CALCULATE(COUNTROWS(fct_matches), fct_matches[result]="home_win")',
            "formatString": "#,0"
        },
        {
            "name": "Victorias Visitante",
            "expression": 'CALCULATE(COUNTROWS(fct_matches), fct_matches[result]="away_win")',
            "formatString": "#,0"
        },
        {
            "name": "Empates",
            "expression": 'CALCULATE(COUNTROWS(fct_matches), fct_matches[result]="draw")',
            "formatString": "#,0"
        },
        {
            "name": "% Victoria Local",
            "expression": "DIVIDE([Victorias Local], [Total Partidos], 0)",
            "formatString": "0.0%"
        },
        {
            "name": "% Victoria Visitante",
            "expression": "DIVIDE([Victorias Visitante], [Total Partidos], 0)",
            "formatString": "0.0%"
        },
        {
            "name": "% Empate",
            "expression": "DIVIDE([Empates], [Total Partidos], 0)",
            "formatString": "0.0%"
        }
    ]

    return measures


def generate_relationships() -> list:
    """Generates star schema relationships"""

    relationships = [
        {
            "name": "rel_fct_tournament",
            "fromTable": "fct_matches",
            "fromColumn": "tournament_id",
            "toTable": "dim_tournaments",
            "toColumn": "tournament_id",
            "isActive": True
        },
        {
            "name": "rel_fct_group",
            "fromTable": "fct_matches",
            "fromColumn": "group_id",
            "toTable": "dim_groups",
            "toColumn": "group_id",
            "isActive": True
        },
        {
            "name": "rel_fct_stadium",
            "fromTable": "fct_matches",
            "fromColumn": "stadium_id",
            "toTable": "dim_stadiums",
            "toColumn": "stadium_id",
            "isActive": True
        },
        {
            "name": "rel_fct_home_team",
            "fromTable": "fct_matches",
            "fromColumn": "home_team_id",
            "toTable": "dim_teams",
            "toColumn": "team_id",
            "isActive": True,
            "crossFilteringBehavior": "bothDirections"
        },
        {
            "name": "rel_fct_away_team",
            "fromTable": "fct_matches",
            "fromColumn": "away_team_id",
            "toTable": "dim_teams",
            "toColumn": "team_id",
            "isActive": False,
            "crossFilteringBehavior": "bothDirections"
        },
        {
            "name": "rel_fct_date",
            "fromTable": "fct_matches",
            "fromColumn": "date_id",
            "toTable": "dim_date",
            "toColumn": "date_id",
            "isActive": True
        }
    ]

    return relationships


def generate_report_json() -> dict:
    """Generates a minimal report.json structure.
    config and filters must be JSON-serialized strings, not objects."""

    report_config = json.dumps({
        "version": "5.48",
        "themeCollection": {
            "baseTheme": {"name": "CY24SU06", "version": "5.48", "type": 2}
        },
        "activeSectionIndex": 0,
        "defaultDrillFilterOtherVisuals": True,
        "allowChangeFilterTypes": True,
        "outspacePane": {"currentSectionIndex": 0, "expanded": False},
        "optionsPane": {"expanded": False},
        "isStickyChangeFilterValues": True,
        "reportWideDoubleClickInteractionType": 0
    }, ensure_ascii=False, separators=(',', ':'))

    section_config = json.dumps(
        {"relationships": [], "objects": {}},
        ensure_ascii=False, separators=(',', ':')
    )

    return {
        "version": "5.48",
        "config": report_config,
        "sections": [
            {
                "name": "ReportSection",
                "displayName": "Euro 2024 Analysis",
                "filters": "[]",
                "ordinal": 0,
                "visualContainers": [],
                "config": section_config
            }
        ],
        "filters": "[]"
    }


if __name__ == "__main__":
    # Example usage (would be called by analytics.py)
    test_config = {
        "host": "localhost",
        "dbname": "tfg_warehouse",
        "user": "postgres",
        "password": "password",
        "port": 5432
    }
    generate_pbip_project(test_config, output_dir=".")
    print("Done!")
