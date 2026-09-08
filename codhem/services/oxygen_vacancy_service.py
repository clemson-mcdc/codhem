import streamlit as st

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
