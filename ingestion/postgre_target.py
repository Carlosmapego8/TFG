# postgres_target.py
import psycopg2
from psycopg2 import sql
from target import DBTarget
import importlib.util
import os
import shutil
import csv

class PostgresTarget(DBTarget):
    """
    DBTarget para PostgreSQL en Windows.
    Permite crear tablas normales, externas CSV y externas PostgreSQL.
    """

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.conn = None
        self.config = None

    def connect(self):
        if self.conn:
            return

        # Cargar configuración
        path = os.path.abspath(self.config_path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}")

        spec = importlib.util.spec_from_file_location("db_config_module", path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)

        if not hasattr(config_module, "DB_CONFIG"):
            raise AttributeError(f"El archivo {path} debe contener un diccionario DB_CONFIG")

        self.config = config_module.DB_CONFIG
        self.conn = psycopg2.connect(**self.config)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

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
            sql.SQL("""CREATE TABLE IF NOT EXISTS {}.{} ({})""").format(
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
        insert_stmt = sql.SQL("""INSERT INTO {}.{} ({}) VALUES ({})""").format(
            sql.Identifier(schema_name),
            sql.Identifier(table_name),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder() * len(columns))
        )
        for row in rows:
            cur.execute(insert_stmt, row)
        self.conn.commit()
        cur.close()

    # ========================
    # TABLAS EXTERNAS CSV
    # ========================
    def create_external_csv_table(self, schema_name, table_name, csv_path):
        """Crea tabla externa CSV para Windows"""
        self.connect()
        cur = self.conn.cursor()

        # Carpeta segura para PostgreSQL
        safe_dir = r"C:\PostgreSQL\csv"
        os.makedirs(safe_dir, exist_ok=True)

        # Copiar CSV al directorio seguro
        safe_path = os.path.join(safe_dir, os.path.basename(csv_path))
        shutil.copy2(csv_path, safe_path)

        # Escapar ruta para SQL
        safe_path_sql = safe_path.replace("\\", "\\\\")

        # Leer cabecera
        with open(safe_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            columns = next(reader)

        columns_sql = ", ".join(f"{c} TEXT" for c in columns)

        sql_statement = f"""
        CREATE EXTENSION IF NOT EXISTS file_fdw;

        CREATE SERVER IF NOT EXISTS csv_server
        FOREIGN DATA WRAPPER file_fdw;

        CREATE FOREIGN TABLE IF NOT EXISTS {schema_name}.{table_name} (
            {columns_sql}
        )
        SERVER csv_server
        OPTIONS (
            filename '{safe_path_sql}',
            format 'csv',
            header 'true'
        );
        """
        cur.execute(sql_statement)
        self.conn.commit()
        cur.close()

    # ========================
    # TABLAS EXTERNAS POSTGRES
    # ========================
    def create_external_postgres_table(
        self,
        schema_name,
        table_name,
        source_schema,
        source_table,
        source_db_config_path
    ):
        """Tabla externa apuntando a otra PostgreSQL usando postgres_fdw"""
        self.connect()
        cur = self.conn.cursor()

        # Cargar config de DB fuente
        path = os.path.abspath(source_db_config_path)
        spec = importlib.util.spec_from_file_location("source_db_config", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        DB_CONFIG = module.DB_CONFIG

        sql_statement = f"""
        CREATE EXTENSION IF NOT EXISTS postgres_fdw;

        CREATE SERVER IF NOT EXISTS remote_pg
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (
            host '{DB_CONFIG['host']}',
            dbname '{DB_CONFIG['dbname']}',
            port '{DB_CONFIG['port']}'
        );

        CREATE USER MAPPING IF NOT EXISTS
        FOR CURRENT_USER
        SERVER remote_pg
        OPTIONS (
            user '{DB_CONFIG['user']}',
            password '{DB_CONFIG['password']}'
        );

        CREATE FOREIGN TABLE IF NOT EXISTS {schema_name}.{table_name}
        SERVER remote_pg
        OPTIONS (
            schema_name '{source_schema}',
            table_name '{source_table}'
        );
        """
        cur.execute(sql_statement)
        self.conn.commit()
        cur.close()
