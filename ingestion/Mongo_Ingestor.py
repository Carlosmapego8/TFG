import json
from bson import ObjectId
from pymongo import MongoClient
from ingestion import Ingestion
from config_loader import load_config


class MongoIngestion(Ingestion):
    def __init__(self, mongo_database: str, mongo_collection: str, schema_name: str, db_target, source_db_config_path: str, table_name=None):
        if table_name is None:
            table_name = mongo_collection

        super().__init__(table_name=table_name, schema_name=schema_name, db_target=db_target)

        self.mongo_database = mongo_database
        self.mongo_collection = mongo_collection
        self.source_db_config_path = source_db_config_path
        self.columns = []
        self.rows = []

    def _build_uri(self, cfg):
        user = cfg.get("username", "")
        pwd = cfg.get("password", "")
        auth_db = cfg.get("authentication_database", "admin")
        if user and pwd:
            return f"mongodb://{user}:{pwd}@{cfg['address']}:{cfg['port']}/{auth_db}"
        return f"mongodb://{cfg['address']}:{cfg['port']}"

    @staticmethod
    def _to_text(value):
        if value is None:
            return None
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, (dict, list)):
            return json.dumps(value, default=str, ensure_ascii=False)
        return str(value)

    def extract(self):
        cfg = load_config(self.source_db_config_path, "MONGO_CONFIG")
        client = MongoClient(self._build_uri(cfg))
        try:
            collection = client[self.mongo_database][self.mongo_collection]

            docs = list(collection.find())
            if not docs:
                raise ValueError(
                    f"La colección {self.mongo_database}.{self.mongo_collection} está vacía."
                )

            seen = {}
            for doc in docs:
                for key in doc.keys():
                    if key not in seen:
                        seen[key] = None
            self.columns = list(seen.keys())

            self.rows = [
                [self._to_text(doc.get(col)) for col in self.columns]
                for doc in docs
            ]
        finally:
            client.close()
