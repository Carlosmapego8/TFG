import csv
from ExternalIngestion import ExternalIngestion

class CSVExternalIngestion(ExternalIngestion):
    def __init__(self, csv_path, schema_name, table_name, db_target):
        super().__init__(schema_name=schema_name, table_name=table_name, db_target=db_target)
        self.csv_path = csv_path
  
    def create_external_table(self):
        
        self.db_target.create_external_csv_table(
            self.schema_name,
            self.table_name,
            self.csv_path
        )
