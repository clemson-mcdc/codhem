import math
import re

import streamlit as st

from codhem.components.periodic_table import ELEMENTS
from codhem.db.client import DatabaseClient
from codhem.models.oxygen_vacancy import (
    OxygenVacancyBaderData,
    OxygenVacancyDisplacementData,
    OxygenVacancyRecord,
    OxygenVacancyVolumeData,
)

COLLECTION_NAME = "oxygen_vacancy_data"
SYSTEM_ORDER = [
    "MgO",
    "MgCuO",
    "MgZnO",
    "MgNiO",
    "MgCoO",
    "MgNiZnO",
    "MgNiCuO",
    "MgCuZnO",
    "MgCoZnO",
    "MgCoNiO",
    "MgCoCuO",
    "MgCuNiZnO",
    "MgCuCoZnO",
    "MgCoNiZnO",
    "MgCoCuNiO",
    "MgCoCuNiZnO",
]
ELEMENT_SYMBOLS = {element["symbol"] for element in ELEMENTS}
HEO_SEARCH_LIMIT = 20
HEO_NUMERIC_FIELDS = {
    "defect_energy": "defect_energy",
    "perfect_energy": "perfect_energy",
    "oxygen_vacancy_energy": "oxygen_vacancy_energy",
    "vacancy_formation_energy": "vacancy_formation_energy",
    "bader_vacancy_nearest_neighbors": "bader.vacancy_nearest_neighbors",
    "bader_total_per_atom": "bader.total_per_atom",
    "bader_volume": "bader.volume",
    "volume_vacancy": "volume.vacancy",
    "volume_perfect": "volume.perfect",
    "volume_difference": "volume.difference",
    "volume_ratio": "volume.ratio",
    "displacement_initial": "displacement.initial",
    "displacement_final": "displacement.final",
    "displacement_difference": "displacement.difference",
}


def _get_collection():
    return DatabaseClient().get_collection(COLLECTION_NAME)


def _to_float(value):
    return float(value) if value is not None else None


def _build_record(document):
    bader = document.get("bader")
    volume = document.get("volume")
    displacement = document.get("displacement")

    return OxygenVacancyRecord(
        system=str(document.get("system", "")),
        vacancy_position=int(document.get("vacancy_position", 0)),
        index=document.get("index"),
        defect_energy=_to_float(document.get("defect_energy")),
        perfect_energy=_to_float(document.get("perfect_energy")),
        oxygen_vacancy_energy=_to_float(document.get("oxygen_vacancy_energy")),
        vacancy_formation_energy=_to_float(document.get("vacancy_formation_energy")),
        neighbor_composition=document.get("neighbor_composition"),
        bader=OxygenVacancyBaderData(
            vacancy_nearest_neighbors=_to_float(bader.get("vacancy_nearest_neighbors")),
            by_element=bader.get("by_element"),
            per_atom=bader.get("per_atom"),
            total_per_atom=_to_float(bader.get("total_per_atom")),
            volume=_to_float(bader.get("volume")),
        )
        if bader
        else None,
        volume=OxygenVacancyVolumeData(
            vacancy=_to_float(volume.get("vacancy")),
            perfect=_to_float(volume.get("perfect")),
            difference=_to_float(volume.get("difference")),
            ratio=_to_float(volume.get("ratio")),
        )
        if volume
        else None,
        displacement=OxygenVacancyDisplacementData(
            initial=_to_float(displacement.get("initial")),
            final=_to_float(displacement.get("final")),
            difference=_to_float(displacement.get("difference")),
        )
        if displacement
        else None,
    )


@st.cache_data(ttl=300)
def get_oxygen_vacancy_systems():
    systems = set(_get_collection().distinct("system"))
    return [system for system in SYSTEM_ORDER if system in systems] + sorted(
        systems.difference(SYSTEM_ORDER)
    )


@st.cache_data(ttl=300)
def get_oxygen_vacancy_system_records(system):
    documents = _get_collection().find(
        {"system": system},
        {"_id": 0},
    ).sort([("vacancy_formation_energy", -1), ("vacancy_position", 1)])
    return [_build_record(document) for document in documents]


def get_average_vacancy_formation_energy(records):
    energies = [
        record.vacancy_formation_energy
        for record in records
        if record.vacancy_formation_energy is not None
    ]
    return sum(energies) / len(energies) if energies else None


def _numeric_range(value):
    if not isinstance(value, dict):
        return {}

    conditions = {}
    for key, operator in (("lt", "$lt"), ("gt", "$gt"), ("eq", "$eq")):
        number = value.get(key)
        if not isinstance(number, int | float) or isinstance(number, bool):
            continue
        try:
            if math.isfinite(number):
                conditions[operator] = number
        except OverflowError:
            continue

    return conditions


def _build_heo_mongo_query(query):
    if not isinstance(query, dict):
        return {}

    mongo_query = {}

    system = query.get("system")
    if isinstance(system, str) and system.strip():
        mongo_query["system"] = {
            "$regex": re.escape(system.strip()),
            "$options": "i",
        }

    vacancy_position = query.get("vacancy_position")
    if isinstance(vacancy_position, int) and not isinstance(vacancy_position, bool):
        mongo_query["vacancy_position"] = vacancy_position

    index = query.get("index")
    if isinstance(index, int) and not isinstance(index, bool):
        mongo_query["index"] = index

    elements_present = query.get("elements_present", [])
    if isinstance(elements_present, str):
        elements_present = [elements_present]
    if isinstance(elements_present, list):
        for element in elements_present[:8]:
            if not isinstance(element, str):
                continue
            symbol = element.strip().capitalize()
            if symbol in ELEMENT_SYMBOLS:
                mongo_query[f"neighbor_composition.{symbol}"] = {"$gt": 0}

    bader_element = query.get("bader_element")
    if isinstance(bader_element, str):
        symbol = bader_element.strip().capitalize()
        if symbol in ELEMENT_SYMBOLS:
            for field_name, mongo_path in (
                ("bader_by_element_value", "bader.by_element"),
                ("bader_per_atom_value", "bader.per_atom"),
            ):
                conditions = _numeric_range(query.get(field_name))
                if conditions:
                    mongo_query[f"{mongo_path}.{symbol}"] = conditions

    for field_name, mongo_field in HEO_NUMERIC_FIELDS.items():
        conditions = _numeric_range(query.get(field_name))
        if conditions:
            mongo_query[mongo_field] = conditions

    return mongo_query


def _build_heo_search_result(document):
    bader = document.get("bader")
    volume = document.get("volume")
    displacement = document.get("displacement")
    bader = bader if isinstance(bader, dict) else {}
    volume = volume if isinstance(volume, dict) else {}
    displacement = displacement if isinstance(displacement, dict) else {}

    return {
        "system": document.get("system"),
        "vacancy_position": document.get("vacancy_position"),
        "index": document.get("index"),
        "neighbor_composition": document.get("neighbor_composition"),
        "defect_energy": document.get("defect_energy"),
        "perfect_energy": document.get("perfect_energy"),
        "oxygen_vacancy_energy": document.get("oxygen_vacancy_energy"),
        "vacancy_formation_energy": document.get("vacancy_formation_energy"),
        "bader": {
            "vacancy_nearest_neighbors": bader.get("vacancy_nearest_neighbors"),
            "by_element": bader.get("by_element"),
            "per_atom": bader.get("per_atom"),
            "total_per_atom": bader.get("total_per_atom"),
            "volume": bader.get("volume"),
        },
        "volume": {
            "vacancy": volume.get("vacancy"),
            "perfect": volume.get("perfect"),
            "difference": volume.get("difference"),
            "ratio": volume.get("ratio"),
        },
        "displacement": {
            "initial": displacement.get("initial"),
            "final": displacement.get("final"),
            "difference": displacement.get("difference"),
        },
    }


def search_heo_vacancy_data(query: dict | None = None, limit: int = 20):
    requested_limit = (
        limit
        if isinstance(limit, int) and not isinstance(limit, bool)
        else HEO_SEARCH_LIMIT
    )
    result_limit = max(1, min(requested_limit, HEO_SEARCH_LIMIT))
    projection = {
        "_id": 0,
        "system": 1,
        "vacancy_position": 1,
        "index": 1,
        "neighbor_composition": 1,
        "defect_energy": 1,
        "perfect_energy": 1,
        "oxygen_vacancy_energy": 1,
        "vacancy_formation_energy": 1,
        "bader.vacancy_nearest_neighbors": 1,
        "bader.by_element": 1,
        "bader.per_atom": 1,
        "bader.total_per_atom": 1,
        "bader.volume": 1,
        "volume.vacancy": 1,
        "volume.perfect": 1,
        "volume.difference": 1,
        "volume.ratio": 1,
        "displacement.initial": 1,
        "displacement.final": 1,
        "displacement.difference": 1,
    }
    documents = (
        _get_collection()
        .find(_build_heo_mongo_query(query), projection)
        .sort([("vacancy_formation_energy", -1), ("vacancy_position", 1)])
        .limit(result_limit)
    )
    return [_build_heo_search_result(document) for document in documents]
