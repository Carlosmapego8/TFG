# postgres_ingestion.py
import psycopg2
from psycopg2 import sql
from ingestion import Ingestion
from config_loader import load_config

class PostgresIngestion(Ingestion):

    def __init__(self, source_table: str, source_schema: str, schema_name: str, db_target, source_db_config_path: str, table_name=None):
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
        config = load_config(self.source_db_config_path, "DB_CONFIG")
        conn = psycopg2.connect(**config)
        cur = conn.cursor()

        query = sql.SQL("SELECT * FROM {}.{}").format(
            sql.Identifier(self.source_schema),
            sql.Identifier(self.source_table)
        )
        cur.execute(query)

        self.columns = [desc[0] for desc in cur.description]
        self.rows = cur.fetchall()

        cur.close()
        conn.close()
