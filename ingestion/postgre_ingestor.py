# postgres_ingestion.py
import psycopg2
from ingestion import Ingestion
import importlib.util
import os

class PostgresIngestion(Ingestion):

    def __init__(self, source_table: str, source_schema: str, schema_name: str, db_target, source_db_config_path: str, table_name=None, db_name=None ):
        if table_name is None:
            table_name = source_table

        super().__init__(table_name=table_name, schema_name=schema_name, db_target=db_target)

        self.source_table = source_table
        self.source_schema = source_schema
        self.source_db_config_path = source_db_config_path
        self.columns = []
        self.rows = []

    def extract(self):
        """
        Obtiene las columnas de la tabla origen (PostgreSQL).
        """
        config = self._load_source_config()
        conn = psycopg2.connect(**config)
        cur = conn.cursor()

        cur.execute(
            f"SELECT * FROM {self.source_schema}.{self.source_table}"
        )

        self.columns = [desc[0] for desc in cur.description]
        self.rows = cur.fetchall()

        cur.close()
        conn.close()

    def _load_source_config(self):
        """
        Carga DB_CONFIG desde el archivo de configuración de la DB origen.
        """
        path = os.path.abspath(self.source_db_config_path)
        spec = importlib.util.spec_from_file_location("source_db_config", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "DB_CONFIG"):
            raise ValueError("El archivo de configuración debe definir DB_CONFIG")

        return module.DB_CONFIG
