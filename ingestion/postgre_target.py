# postgres_target.py
import psycopg2
from psycopg2 import sql
from target import DBTarget
import os
import shutil
import csv
from config_loader import load_config

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

        self.config = load_config(self.config_path, "DB_CONFIG")
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

        DB_CONFIG = load_config(source_db_config_path, "DB_CONFIG")

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

    # ========================
    # TABLAS EXTERNAS MONGO
    # ========================
    def create_external_mongo_table(
        self,
        schema_name,
        table_name,
        mongo_database,
        mongo_collection,
        columns,
        source_db_config_path
    ):
        """Tabla externa apuntando a MongoDB usando mongo_fdw"""
        self.connect()
        cur = self.conn.cursor()

        MONGO_CONFIG = load_config(source_db_config_path, "MONGO_CONFIG")

        columns_sql = ",\n            ".join(f"{col} {typ}" for col, typ in columns)

        sql_statement = f"""
        CREATE EXTENSION IF NOT EXISTS mongo_fdw;

        CREATE SERVER IF NOT EXISTS remote_mongo
        FOREIGN DATA WRAPPER mongo_fdw
        OPTIONS (
            address '{MONGO_CONFIG['address']}',
            port '{MONGO_CONFIG['port']}'
        );

        CREATE USER MAPPING IF NOT EXISTS
        FOR CURRENT_USER
        SERVER remote_mongo
        OPTIONS (
            username '{MONGO_CONFIG['username']}',
            password '{MONGO_CONFIG['password']}'
        );

        CREATE FOREIGN TABLE IF NOT EXISTS {schema_name}.{table_name} (
            {columns_sql}
        )
        SERVER remote_mongo
        OPTIONS (
            database '{mongo_database}',
            collection '{mongo_collection}'
        );
        """
        cur.execute(sql_statement)
        self.conn.commit()
        cur.close()
