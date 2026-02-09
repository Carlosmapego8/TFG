from abc import ABC, abstractmethod

class DBTarget(ABC):
    """
    Interfaz para una base de datos destino.
    """

    @abstractmethod
    def connect(self):
        """Establecer conexión con la base de datos destino."""
        pass

    @abstractmethod
    def create_schema(self, schema_name: str):
        """Crear un esquema en la base de datos destino."""
        pass

    @abstractmethod
    def create_table(self, schema_name: str, table_name: str, columns: list[str]):
        """Crear una tabla en el esquema especificado con las columnas dadas."""
        pass

    @abstractmethod
    def insert_rows(self, schema_name: str, table_name: str, columns: list[str], rows: list[list]):
        """Insertar filas en la tabla especificada."""
        pass
