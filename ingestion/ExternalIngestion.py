from abc import ABC, abstractmethod

class ExternalIngestion(ABC):
    def __init__(self, table_name: str, schema_name: str = "raw", db_target=None):
        self.schema_name = schema_name
        self.table_name = table_name
        self.db_target = db_target
        
    @abstractmethod
    def create_external_table(self):
        pass

    def run(self):
        self.db_target.create_schema(self.schema_name)
        self.create_external_table()