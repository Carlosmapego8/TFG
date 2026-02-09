from abc import ABC, abstractmethod

class Ingestion(ABC):
    """
    Clase base de ingesto de datos.
    """

    def __init__(self, table_name: str, schema_name: str = "raw", db_target=None):
        self.schema_name = schema_name
        self.table_name = table_name
        self.db_target = db_target

    @abstractmethod
    def extract(self):
        """
        Extrae datos y los guarda en la Target DB
        """
        pass

    def load(self):
        """
        Lógica común de carga: usa la BD destino.
        """
        self.db_target.create_schema(self.schema_name)
        self.db_target.create_table(self.schema_name, self.table_name, self.headers)
        self.db_target.insert_rows(self.schema_name, self.table_name, self.headers, self.rows)
        self.db_target.close()

    def run(self):
        """Ejecuta el proceso completo de extracción y carga."""
        self.extract()
        self.load()
    
    def add_db_target(self, db_target):
        """Set the database target for this ingestion."""
        self.db_target = db_target
