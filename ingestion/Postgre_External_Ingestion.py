from ExternalIngestion import ExternalIngestion


class PostgresExternalIngestion(ExternalIngestion):

    def __init__(self, source_schema: str, source_table: str, schema_name: str, table_name, db_target, source_db_config_path: str):
        if table_name is None:
            table_name = source_table

        super().__init__(schema_name=schema_name, table_name=table_name, db_target=db_target)

        self.source_schema = source_schema
        self.source_table = source_table
        self.source_db_config_path = source_db_config_path

    def create_external_table(self):
        self.db_target.create_external_postgres_table(
            self.schema_name,
            self.table_name,
            self.source_schema,
            self.source_table,
            self.source_db_config_path
        )
