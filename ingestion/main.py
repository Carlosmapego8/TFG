import yaml
import traceback
import os 
import shutil


from orchestrator import Orchestrator
from postgre_target import PostgresTarget
from CSV_Ingestor import CSVIngestion
from postgre_ingestor import PostgresIngestion
from CSV_External_Ingestion import CSVExternalIngestion
from Postgre_External_Ingestion import PostgresExternalIngestion


def main():
    db_target = None
    try:
        # Leer YAML
        try:
            with open("pipeline_config.yml", "r") as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error leyendo YAML: {e}")
            return

        # Crear DB Target
        try:
            db_target = PostgresTarget(config["database"]["config_file"])
        except Exception as e:
            print(f"❌ Error inicializando PostgresTarget: {e}")
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
            else:
                raise ValueError(f"Tipo de ingesta no soportado: {ing_type}")

        if not ingestions:
            print("⚠️ No hay ingestas definidas")
            return

        # Orchestrator
        orchestrator = Orchestrator(
            ingestions=ingestions,
            transformations=config.get("transformations", []),
            analytics=config.get("analytics")
        )

        # Ejecutar
        orchestrator.run()
        print("✅ Pipeline ejecutado correctamente")

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        traceback.print_exc()
    finally:
        if db_target:
            try:
                db_target.close()
            except Exception as e:
                print(f"⚠️ Error cerrando conexión: {e}")


if __name__ == "__main__":
    main()
