from pymongo import MongoClient

from codhem.config.settings import get_settings
from codhem.models.domain import ScientificRecord


class DatabaseClient:
    def __init__(self):
        settings = get_settings()
        connection_url = (
            f"mongodb://{settings.database.username}:{settings.database.password}"
            f"@{settings.database.host}:{settings.database.port}/"
        )
        if not settings.database.username:
            connection_url = (
                f"mongodb://{settings.database.host}:{settings.database.port}/"
            )

        self.client = MongoClient(connection_url)
        self.database = self.client[settings.database.name]

    def get_collection(self, collection_name: str):
        return self.database[collection_name]

    def fetch_records(self):
        return [
            ScientificRecord(
                dataset_id="DS-001",
                material="Copper",
                temperature=25.0,
                signal=11.2,
                instrument="Spectrometer",
            ),
            ScientificRecord(
                dataset_id="DS-002",
                material="Graphene",
                temperature=120.0,
                signal=18.7,
                instrument="Probe Station",
            ),
            ScientificRecord(
                dataset_id="DS-003",
                material="Silicon",
                temperature=240.0,
                signal=13.4,
                instrument="Microscope",
            ),
        ]
