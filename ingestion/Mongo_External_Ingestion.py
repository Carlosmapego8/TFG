from ExternalIngestion import ExternalIngestion
from pymongo import MongoClient
from bson import ObjectId
from config_loader import load_config

class MongoExternalIngestion(ExternalIngestion):

    # Mapeo de tipos Python/BSON a tipos PostgreSQL
    BSON_TO_PG = {
        str: "text",
        int: "int",
        float: "float8",
        bool: "boolean",
        list: "json",
        dict: "json",
        ObjectId: "name",
    }

    def __init__(self, mongo_database, mongo_collection, schema_name, table_name, db_target, source_db_config_path):
        if table_name is None:
            table_name = mongo_collection

        super().__init__(schema_name=schema_name, table_name=table_name, db_target=db_target)

        self.mongo_database = mongo_database
        self.mongo_collection = mongo_collection
        self.source_db_config_path = source_db_config_path

        # Cargar config de MongoDB
        config = load_config(source_db_config_path, "MONGO_CONFIG")
        self.address = config["address"]
        self.port = config["port"]
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        self.authentication_database = config.get("authentication_database", "admin")

        # Autodescubrir schema
        self.columns = self._discover_schema()

    def _discover_schema(self):
        """Conecta a MongoDB y descubre el schema a partir de un documento de muestra."""
        if self.username and self.password:
            uri = f"mongodb://{self.username}:{self.password}@{self.address}:{self.port}/{self.authentication_database}"
        else:
            uri = f"mongodb://{self.address}:{self.port}"

        client = MongoClient(uri)
        db = client[self.mongo_database]
        collection = db[self.mongo_collection]

        sample = collection.find_one()
        client.close()

        if sample is None:
            raise ValueError(
                f"La colección {self.mongo_database}.{self.mongo_collection} está vacía. "
                "No se puede autodescubrir el schema."
            )

        # _id siempre primero con tipo name (requisito de mongo_fdw)
        columns = [("_id", "name")]

        for key, value in sample.items():
            if key == "_id":
                continue
            pg_type = self.BSON_TO_PG.get(type(value), "text")
            columns.append((key, pg_type))

        return columns

    def create_external_table(self):
        self.db_target.create_external_mongo_table(
            self.schema_name,
            self.table_name,
            self.mongo_database,
            self.mongo_collection,
            self.columns,
            self.source_db_config_path
        )
