import psycopg2
from ExternalIngestion import ExternalIngestion
from config_loader import load_config


class PostgresExternalIngestion(ExternalIngestion):

    def __init__(self, source_schema: str, source_table: str, schema_name: str, table_name, db_target, source_db_config_path: str):
        if table_name is None:
            table_name = source_table

        super().__init__(schema_name=schema_name, table_name=table_name, db_target=db_target)

        self.source_schema = source_schema
        self.source_table = source_table
        self.source_db_config_path = source_db_config_path
        self.columns = self._discover_schema()

    def _discover_schema(self):
        config = load_config(self.source_db_config_path, "DB_CONFIG")
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT column_name, udt_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
            """,
            (self.source_schema, self.source_table),
        )
        cols = cur.fetchall()
        cur.close()
        conn.close()
        if not cols:
            raise ValueError(
                f"La tabla {self.source_schema}.{self.source_table} no existe o no tiene columnas en el origen."
            )
        return cols

    def create_external_table(self):
        self.db_target.create_external_postgres_table(
            self.schema_name,
            self.table_name,
            self.source_schema,
            self.source_table,
            self.columns,
            self.source_db_config_path
        )
