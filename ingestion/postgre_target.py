# postgres_target.py
import psycopg2
from psycopg2 import sql
from target import DBTarget
import importlib.util
import os

class PostgresTarget(DBTarget):
    """
    Implementación de DBTarget para PostgreSQL.
    Permite pasar un archivo de configuración con DB_CONFIG.
    """

    def __init__(self, config_path: str):
        """
        :param config_path: ruta al archivo db_config.py que define DB_CONFIG
        """
        self.config_path = config_path
        self.conn = None
        self.config = None

    def connect(self):
        """
        Carga DB_CONFIG desde el archivo y abre la conexión.
        """
        if self.conn:
            return

        # Comprobar que existe el archivo
        path = os.path.abspath(self.config_path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}")

        # Cargar módulo dinámicamente
        spec = importlib.util.spec_from_file_location("db_config_module", path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)

        # Verificar que contenga DB_CONFIG
        if not hasattr(config_module, "DB_CONFIG"):
            raise AttributeError(f"El archivo {path} debe contener un diccionario DB_CONFIG")

        self.config = config_module.DB_CONFIG

        # Abrir conexión
        self.conn = psycopg2.connect(**self.config)

    def create_schema(self, schema_name: str):
        self.connect()
        cur = self.conn.cursor()
        cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema_name)))
        self.conn.commit()
        cur.close()

    def create_table(self, schema_name: str, table_name: str, columns: list[str]):
        self.connect()
        cur = self.conn.cursor()
        cur.execute(
            sql.SQL("""
                CREATE TABLE IF NOT EXISTS {}.{} (
                    {}
                )
            """).format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
                sql.SQL(", ").join(sql.SQL("{} TEXT").format(sql.Identifier(c)) for c in columns)
            )
        )
        self.conn.commit()
        cur.close()

    def insert_rows(self, schema_name: str, table_name: str, columns: list[str], rows: list[list]):
        self.connect()
        cur = self.conn.cursor()
        insert_stmt = sql.SQL("""
            INSERT INTO {}.{} ({})
            VALUES ({})
        """).format(
            sql.Identifier(schema_name),
            sql.Identifier(table_name),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder() * len(columns))
        )
        for row in rows:
            cur.execute(insert_stmt, row)
        self.conn.commit()
        cur.close()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
