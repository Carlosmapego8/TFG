import yaml
from CSV_Ingestor import CSVIngestion
from postgre_target import PostgresTarget
from orchestrator import Orchestrator

def main():
    # 1️ Leer configuración del YAML
    with open("pipeline_config.yml") as f:
        config = yaml.safe_load(f)

    # 2️ Crear DBTarget usando config_file
    db_config_file = config['database']['config_file']
    db_target = PostgresTarget(db_config_file)

    # 3️ Crear ingestions
    ingestions = []
    for ing_conf in config['ingestions']:
        if ing_conf['type'] == 'csv':
            csv_path = ing_conf['path']
            table_name = ing_conf.get('table_name')
            schema_name = ing_conf.get('schema_name', config['database'].get('default_schema', 'raw'))

            ingestor = CSVIngestion(
                csv_path=csv_path,
                schema_name=schema_name,
                db_target=db_target,
                table_name=table_name
            )
            ingestions.append(ingestor)

    # 4️ Crear Orchestrator con ingestions
    orchestrator = Orchestrator(
        ingestions=ingestions,
        transformations=config.get('transformations', []),
        analytics=config.get('analytics')
    )

    # 5️ Ejecutar pipeline
    orchestrator.run()

    # 6️ Cerrar conexión
    db_target.close()
    print("✅ Pipeline completado usando YAML y Orchestrator")

if __name__ == "__main__":
    main()
