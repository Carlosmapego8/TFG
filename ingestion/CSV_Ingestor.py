import csv
import os
from ingestion import Ingestion

class CSVIngestion(Ingestion):
    def __init__(self, csv_path: str, schema_name: str, db_target, table_name=None, db_name=None):
        
        if table_name is None:
            table_name = self.get_table_name(csv_path)

        super().__init__(table_name=table_name, schema_name=schema_name, db_target=db_target)
        self.csv_path = csv_path
        self.columns = []
        self.rows = []

    @staticmethod
    def get_table_name(csv_path: str) -> str:
        return os.path.splitext(os.path.basename(csv_path))[0].lower()

    def extract(self):
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            self.columns = next(reader)
            self.rows = list(reader)
