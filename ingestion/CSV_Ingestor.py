import csv
import os
import sys
import psycopg2
from psycopg2 import sql
from db_config import DB_CONFIG


def get_table_name(csv_path: str) -> str:
    """
    Usa el nombre del archivo CSV como nombre de tabla
    """

    return os.path.splitext(os.path.basename(csv_path))[0].lower()

def main(csv_path: str, schema_name: str = "public"):
    table_name = get_table_name(csv_path)

    # Conexión a la base de datos
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)  # Primera fila = nombres de columnas

        # Crear esquema si no existe
        create_schema = sql.SQL("CREATE SCHEMA IF NOT EXISTS {schema}").format(
            schema=sql.Identifier(schema_name)
        )
        cur.execute(create_schema)

        # Crear tabla en esquema especificado
        create_table = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {schema}.{table} (
                {columns}
            )
        """).format(
            schema=sql.Identifier(schema_name),
            table=sql.Identifier(table_name),
            columns=sql.SQL(", ").join(
                sql.SQL("{} TEXT").format(sql.Identifier(col))
                for col in headers
            )
        )
        cur.execute(create_table)

        # Insertar filas
        insert_stmt = sql.SQL("""
            INSERT INTO {schema}.{table} ({fields})
            VALUES ({values})
        """).format(
            schema=sql.Identifier(schema_name),
            table=sql.Identifier(table_name),
            fields=sql.SQL(", ").join(map(sql.Identifier, headers)),
            values=sql.SQL(", ").join(sql.Placeholder() * len(headers))
        )

        for row in reader:
            cur.execute(insert_stmt, row)

    conn.commit()
    cur.close()
    conn.close()

    print(f"CSV '{csv_path}' cargado en la tabla '{schema_name}.{table_name}'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python CSV_Ingestor.py archivo.csv [esquema]")
        sys.exit(1)

    csv_file = sys.argv[1]
    schema = sys.argv[2] if len(sys.argv) > 2 else "public"

    main(csv_file, schema)