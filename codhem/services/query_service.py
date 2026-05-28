from codhem.db.client import DatabaseClient
from codhem.models.domain import ScientificRecord
from codhem.models.filters import FilterCriteria


def fetch_filtered_records(criteria: FilterCriteria):
    client = DatabaseClient()
    records = client.fetch_records()
    return [
        record
        for record in records
        if isinstance(record, ScientificRecord)
        and (criteria.material == "All" or record.material == criteria.material)
        and (criteria.instrument == "All" or record.instrument == criteria.instrument)
        and criteria.min_temperature <= record.temperature <= criteria.max_temperature
    ]
