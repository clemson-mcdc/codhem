import pandas as pd
import streamlit as st

from codhem.db.client import DatabaseClient


COLLECTION_NAME = "literature_data"
PROPERTY_PATHS = {
    "rho": "density",
    "elastic_modulus": "mechanical_properties.elastic_modulus",
    "sigma_at_23_c": "mechanical_properties.sigma_at_23_c",
    "sigma_at_1000_c": "mechanical_properties.sigma_at_1000_c",
    "sigma_at_1200_c": "mechanical_properties.sigma_at_1200_c",
    "shear_modulus": "mechanical_properties.shear_modulus",
    "c11": "mechanical_properties.c11",
    "ductility": "mechanical_properties.ductility",
}


def _get_literature_collection():
    client = DatabaseClient()
    return client.get_collection(COLLECTION_NAME)


@st.cache_data(ttl=300)
def get_literature_elements():
    collection = _get_literature_collection()
    symbols = set()
    for document in collection.find({}, {"_id": 0, "element_composition": 1}):
        symbols.update(
            symbol.capitalize()
            for symbol in document.get("element_composition", {}).keys()
        )
    return sorted(symbol for symbol in symbols if symbol)


@st.cache_data(ttl=300)
def get_literature_phase_options():
    return ["FCC", "BCC", "Other"]


def _build_phase_query(phase_value):
    phase_fields = [
        "phase_data.phase",
        "phase_data.type_of_phase",
        "phase_data.types_of_phases",
    ]
    if phase_value == "FCC":
        return {
            "$or": [
                {field_name: {"$regex": "FCC", "$options": "i"}}
                for field_name in phase_fields
            ]
        }
    if phase_value == "BCC":
        return {
            "$or": [
                {field_name: {"$regex": "BCC", "$options": "i"}}
                for field_name in phase_fields
            ]
        }
    if phase_value == "Other":
        return {
            "$nor": [
                {field_name: {"$regex": "FCC", "$options": "i"}}
                for field_name in phase_fields
            ]
            + [
                {field_name: {"$regex": "BCC", "$options": "i"}}
                for field_name in phase_fields
            ]
        }
    return None


def _build_range_query(field_name, range_filter):
    query = {}
    minimum = range_filter.get("minimum")
    maximum = range_filter.get("maximum")
    if minimum is not None:
        query["$gte"] = minimum
    if maximum is not None:
        query["$lte"] = maximum
    if query:
        return {field_name: query}
    return None


def _build_literature_query(selected_elements, filter_state):
    clauses = []

    if selected_elements:
        clauses.extend(
            {f"element_composition.{element.lower()}": {"$exists": True}}
            for element in selected_elements
        )

    phase_value = filter_state.get("phase")
    if phase_value:
        phase_clause = _build_phase_query(phase_value)
        if phase_clause is not None:
            clauses.append(phase_clause)

    for property_key, range_filter in filter_state.get("property_ranges", {}).items():
        field_name = PROPERTY_PATHS[property_key]
        clause = _build_range_query(field_name, range_filter)
        if clause is not None:
            clauses.append(clause)

    for element, range_filter in filter_state.get("composition_ranges", {}).items():
        clause = _build_range_query(
            f"element_composition.{element.lower()}",
            range_filter,
        )
        if clause is not None:
            clauses.append(clause)

    if not clauses:
        return {}
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def _get_phase_value(document):
    phase_data = document.get("phase_data", {})
    return (
        phase_data.get("phase")
        or phase_data.get("type_of_phase")
        or phase_data.get("types_of_phases")
        or ""
    )


def _flatten_literature_document(document):
    mechanical_properties = document.get("mechanical_properties", {})
    test_data = document.get("test_data", {})

    return {
        "Unique ID": document.get("unique_id", ""),
        "Composition": document.get("composition", ""),
        "DOI": document.get("doi", ""),
        "Phase": _get_phase_value(document),
        "ρ (g/cm3)": document.get("density"),
        "E (GPa)": mechanical_properties.get("elastic_modulus"),
        "σ (MPa) at 23 C": mechanical_properties.get("sigma_at_23_c"),
        "σ (MPa) at 1000 C": mechanical_properties.get("sigma_at_1000_c"),
        "σ (MPa) at 1200 C": mechanical_properties.get("sigma_at_1200_c"),
        "G (GPa)": mechanical_properties.get("shear_modulus"),
        "C11 (GPa)": mechanical_properties.get("c11"),
        "Fracture Toughness": mechanical_properties.get("fracture_toughness"),
        "Ductility [%]": mechanical_properties.get("ductility"),
        "Test Type": test_data.get("type_of_test", ""),
    }


@st.cache_data(ttl=300)
def query_literature_data(
    selected_elements,
    phase,
    property_ranges,
    composition_ranges,
):
    filter_state = {
        "phase": phase,
        "property_ranges": property_ranges,
        "composition_ranges": composition_ranges,
    }
    query = _build_literature_query(selected_elements, filter_state)

    collection = _get_literature_collection()
    documents = list(
        collection.find(
            query,
            {
                "_id": 0,
                "unique_id": 1,
                "composition": 1,
                "doi": 1,
                "density": 1,
                "element_composition": 1,
                "phase_data": 1,
                "mechanical_properties": 1,
                "test_data": 1,
            },
        )
    )
    rows = [_flatten_literature_document(document) for document in documents]
    return pd.DataFrame(rows)


def search_literature_data(query: dict | None = None, limit: int = 5):
    query = query or {}
    if not isinstance(query, dict):
        return []

    clauses = []

    composition = str(query.get("composition", "")).strip()
    if composition:
        clauses.append({"composition": {"$regex": composition, "$options": "i"}})

    doi = str(query.get("doi", "")).strip()
    if doi:
        clauses.append({"doi": {"$regex": doi, "$options": "i"}})

    record_id = str(query.get("record_id", "")).strip()
    if record_id:
        clauses.append({"unique_id": {"$regex": record_id, "$options": "i"}})

    phase = str(query.get("phase", "")).strip()
    if phase:
        clauses.append(
            {
                "$or": [
                    {"phase_data.phase": {"$regex": phase, "$options": "i"}},
                    {
                        "phase_data.type_of_phase": {
                            "$regex": phase,
                            "$options": "i",
                        }
                    },
                    {
                        "phase_data.types_of_phases": {
                            "$regex": phase,
                            "$options": "i",
                        }
                    },
                ]
            }
        )

    test_type = str(query.get("test_type", "")).strip()
    if test_type:
        clauses.append(
            {"test_data.type_of_test": {"$regex": test_type, "$options": "i"}}
        )

    elements_present = query.get("elements_present", [])
    if isinstance(elements_present, str):
        elements_present = [elements_present]
    if isinstance(elements_present, list):
        for element in elements_present:
            normalized_element = str(element).strip().lower()
            if normalized_element:
                clauses.append(
                    {f"element_composition.{normalized_element}": {"$exists": True}}
                )

    density_min = query.get("density_min")
    density_max = query.get("density_max")
    density_range = {}
    if isinstance(density_min, int | float):
        density_range["$gte"] = density_min
    if isinstance(density_max, int | float):
        density_range["$lte"] = density_max
    if density_range:
        clauses.append({"density": density_range})

    elastic_modulus_min = query.get("elastic_modulus_min")
    elastic_modulus_max = query.get("elastic_modulus_max")
    elastic_modulus_range = {}
    if isinstance(elastic_modulus_min, int | float):
        elastic_modulus_range["$gte"] = elastic_modulus_min
    if isinstance(elastic_modulus_max, int | float):
        elastic_modulus_range["$lte"] = elastic_modulus_max
    if elastic_modulus_range:
        clauses.append({"mechanical_properties.elastic_modulus": elastic_modulus_range})

    mongo_query = {} if not clauses else clauses[0] if len(clauses) == 1 else {"$and": clauses}
    documents = list(
        _get_literature_collection().find(
            mongo_query,
            {
                "_id": 0,
                "unique_id": 1,
                "composition": 1,
                "doi": 1,
                "density": 1,
                "phase_data": 1,
                "mechanical_properties": 1,
                "test_data": 1,
            },
        ).limit(max(1, min(limit, 10)))
    )

    return [_flatten_literature_document(document) for document in documents]
