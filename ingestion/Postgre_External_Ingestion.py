from ExternalIngestion import ExternalIngestion

class PostgresExternalIngestion(ExternalIngestion):

    def create_external_table(self):
        sql = f"""
        CREATE EXTENSION IF NOT EXISTS postgres_fdw;

        CREATE SERVER IF NOT EXISTS remote_pg
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (
            host '{self.host}',
            dbname '{self.dbname}',
            port '{self.port}'
        );

        CREATE USER MAPPING IF NOT EXISTS
        FOR CURRENT_USER
        SERVER remote_pg
        OPTIONS (
            user '{self.user}',
            password '{self.password}'
        );

        CREATE FOREIGN TABLE IF NOT EXISTS {self.schema_name}.{self.table_name}
        SERVER remote_pg
        OPTIONS (
            schema_name '{self.source_schema}',
            table_name '{self.source_table}'
        );
        """

        self.db_target.execute(sql)
