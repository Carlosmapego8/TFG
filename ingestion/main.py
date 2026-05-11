import yaml
import traceback
import os
import shutil
import sys
from pathlib import Path


from orchestrator import Orchestrator
from postgre_target import PostgresTarget
from CSV_Ingestor import CSVIngestion
from postgre_ingestor import PostgresIngestion
from CSV_External_Ingestion import CSVExternalIngestion
from Postgre_External_Ingestion import PostgresExternalIngestion
from Mongo_External_Ingestion import MongoExternalIngestion

# Import Analytics from analysis module
sys.path.insert(0, str(Path(__file__).parent.parent))
from analysis.analytics import Analytics


def main():
    db_target = None
    try:
        # Leer YAML
        try:
            with open("pipeline_config.yml", "r") as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"[ERROR] Error leyendo YAML: {e}")
            return

        # Crear DB Target
        try:
            db_target = PostgresTarget(config["database"]["config_file"])
        except Exception as e:
            print(f"[ERROR] Error inicializando PostgresTarget: {e}")
            traceback.print_exc()
            return

        # Crear ingestas según tipo
        ingestions = []

        for ing in config.get("ingestions", []):
            ing_type = ing.get("type")

            if ing_type == "csv":
                ingestions.append(
                    CSVIngestion(
                        csv_path=ing["path"],
                        schema_name=ing["schema_name"],
                        table_name=ing.get("table_name"),
                        db_target=db_target
                    )
                )
            elif ing_type == "postgres":
                ingestions.append(
                    PostgresIngestion(
                        source_schema=ing["source_schema"],
                        source_table=ing["source_table"],
                        schema_name=ing["schema_name"],
                        table_name=ing.get("table_name"),
                        db_target=db_target,
                        source_db_config_path=ing["source_db_config"]
                    )
                )
            elif ing_type == "csv_external":

                ingestions.append(
                    CSVExternalIngestion(
                        csv_path=ing["path"],
                        schema_name=ing["schema_name"],
                        table_name=ing.get("table_name"),
                        db_target=db_target
                    )
                )
            elif ing_type == "postgres_external":
                ingestions.append(
                    PostgresExternalIngestion(
                        source_schema=ing["source_schema"],
                        source_table=ing["source_table"],
                        schema_name=ing["schema_name"],
                        table_name=ing.get("table_name"),
                        db_target=db_target,
                        source_db_config_path=ing["source_db_config"]
                    )
                )
            elif ing_type == "mongo_external":
                ingestions.append(
                    MongoExternalIngestion(
                        mongo_database=ing["mongo_database"],
                        mongo_collection=ing["mongo_collection"],
                        schema_name=ing["schema_name"],
                        table_name=ing.get("table_name"),
                        db_target=db_target,
                        source_db_config_path=ing["source_db_config"]
                    )
                )
            else:
                raise ValueError(f"Tipo de ingesta no soportado: {ing_type}")

        if not ingestions:
            print("[WARN] No hay ingestas definidas")
            return

        # Crear componente Analytics si está configurado
        analytics_instance = None
        analytics_config = config.get("analytics")

        if analytics_config:
            try:
                print("\n[INFO] Configurando componente Analytics...")
                analytics_instance = Analytics(
                    db_config_path=analytics_config.get("db_config_path",
                                                        config["database"]["config_file"]),
                    output_dir=analytics_config.get("output_dir", "analysis"),
                    project_name=analytics_config.get("project_name", "euro_analysis")
                )
                print("[OK] Componente Analytics configurado")
            except Exception as e:
                print(f"[WARN] Error configurando Analytics: {e}")
                print("[INFO] El pipeline continuará sin Analytics")
                traceback.print_exc()

        # Orchestrator
        orchestrator = Orchestrator(
            ingestions=ingestions,
            transformations=config.get("transformations", []),
            analytics=analytics_instance
        )

        # Ejecutar
        print("\n" + "="*70)
        print("INICIANDO PIPELINE DE DATOS")
        print("="*70)
        orchestrator.run()
        print("\n" + "="*70)
        print("[OK] Pipeline ejecutado correctamente")
        print("="*70 + "\n")

    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        traceback.print_exc()
    finally:
        if db_target:
            try:
                db_target.close()
            except Exception as e:
                print(f"[WARN] Error cerrando conexión: {e}")


if __name__ == "__main__":
    main()
