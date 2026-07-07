from dataclasses import asdict
import streamlit as st
import pandas as pd
from pathlib import Path

from codhem.components.periodic_table import ELEMENTS
from codhem.db.client import DatabaseClient
from codhem.models.domain import DftCalculation


COLLECTION_NAME = "dft_calculations"
ELEMENT_SYMBOLS = [element["symbol"] for element in ELEMENTS]
DATA_ROOT = Path("data")


def list_dft_calculations():
    collection = DatabaseClient().get_collection(COLLECTION_NAME)
    documents = collection.find({}).sort("alloy", 1)
    records = []

    for document in documents:
        unique_id = document.get("unique_id", "")
        data_paths = {"contcar": None, "pdos": None, "tdos": None}
        if unique_id:
            for key in data_paths:
                path = DATA_ROOT / key / unique_id
                if path.exists():
                    data_paths[key] = str(path)

        records.append(
            DftCalculation(
                mongo_id=str(document.get("_id", "")),
                unique_id=unique_id,
                user=document.get("user", ""),
                directory=document.get("directory", ""),
                path=document.get("path", ""),
                alloy=document.get("alloy", ""),
                atom_count=int(document.get("atom_count", 0) or 0),
                structure=document.get("structure", ""),
                potcar=document.get("potcar", ""),
                lattice_params=document.get("lattice_params", {}),
                vol_per_atom=document.get("vol_per_atom"),
                local_lattice_distortion=document.get("local_lattice_distortion"),
                fermi_energy=document.get("fermi_energy"),
                dos_at_fermi=document.get("dos_at_fermi", {}),
                bonding_area=document.get("bonding_area"),
                antibonding_area=document.get("antibonding_area"),
                d_band_center=document.get("d_band_center"),
                element_composition=document.get("element_composition", {}),
                structure_counts=document.get("structure_counts", {}),
                data=data_paths,
                elastic_constants=document.get("elastic_constants", {}),
                shear_modulus=document.get("shear_modulus", {}),
                bulk_modulus=document.get("bulk_modulus"),
                youngs_modulus=document.get("youngs_modulus", {}),
                poisson_ratio=document.get("poisson_ratio"),
                pugh_ratio=document.get("pugh_ratio"),
            )
        )

    return records


@st.cache_data
def build_dft_calculations_dashboard_dataframe():
    records = list_dft_calculations()
    rows = []

    for record in records:
        row = asdict(record)
        row["_id"] = row.pop("mongo_id")
        row["unique_id"] = row["unique_id"] or row["_id"]

        composition = row["element_composition"] if isinstance(row["element_composition"], dict) else {}
        normalized_composition = {
            symbol.upper(): value
            for symbol, value in composition.items()
        }
        element_symbols = [symbol.capitalize() for symbol in normalized_composition.keys()]

        elastic_values = list(row["elastic_constants"].values())
        shear_values = list(row["shear_modulus"].values())
        youngs_values = list(row["youngs_modulus"].values())
        has_elastic = all(
            value is not None
            for value in elastic_values
            + shear_values
            + youngs_values
            + [row["bulk_modulus"], row["poisson_ratio"], row["pugh_ratio"]]
        )

        row["element_composition"] = composition
        row["element_symbols"] = element_symbols
        row["element_count"] = len(element_symbols)
        row["complexity"] = (
            ["Pure", "Binary", "Ternary", "Quaternary", "Quinary"][len(element_symbols) - 1]
            if 1 <= len(element_symbols) <= 5
            else ">5 elements"
        )
        row["has_elastic"] = has_elastic
        row["inv_pugh"] = (1 / row["pugh_ratio"]) if row["pugh_ratio"] not in (None, 0) else None

        for symbol in ELEMENT_SYMBOLS:
            row[f"{symbol}_comp"] = normalized_composition.get(symbol.upper(), 0)
            row[f"{symbol}_present"] = int(row[f"{symbol}_comp"] > 0)

        rows.append(row)

    return pd.DataFrame(rows)



def _build_dft_result_row(row):
    data_paths = row.get("data") if isinstance(row.get("data"), dict) else {}
    shear_modulus = row.get("shear_modulus")
    youngs_modulus = row.get("youngs_modulus")
    shear_modulus_average = None
    youngs_modulus_e_vrh = None

    if isinstance(shear_modulus, dict):
        average_value = shear_modulus.get("average")
        if isinstance(average_value, (int, float)):
            shear_modulus_average = float(average_value)

    if isinstance(youngs_modulus, dict):
        e_vrh_value = youngs_modulus.get("e_vrh")
        if isinstance(e_vrh_value, (int, float)):
            youngs_modulus_e_vrh = float(e_vrh_value)

    return {
        "unique_id": row.get("unique_id", ""),
        "alloy": row.get("alloy", ""),
        "structure": row.get("structure", ""),
        "atom_count": row.get("atom_count"),
        "complexity": row.get("complexity", ""),
        "has_elastic": bool(row.get("has_elastic", False)),
        "elements_present": row.get("element_symbols", []),
        "fermi_energy": row.get("fermi_energy"),
        "bulk_modulus": row.get("bulk_modulus"),
        "poisson_ratio": row.get("poisson_ratio"),
        "pugh_ratio": row.get("pugh_ratio"),
        "dos_at_fermi": row.get("dos_at_fermi"),
        "shear_modulus_average": shear_modulus_average,
        "youngs_modulus_e_vrh": youngs_modulus_e_vrh,
        "data_available": {
            "contcar": bool(data_paths.get("contcar")),
            "pdos": bool(data_paths.get("pdos")),
            "tdos": bool(data_paths.get("tdos")),
        },
    }


def search_dft_calculations(query: dict | None = None, limit: int = 5):
    query = query or {}
    if not isinstance(query, dict):
        return []

    dataframe = build_dft_calculations_dashboard_dataframe().copy()

    alloy = str(query.get("alloy", "")).strip()
    if alloy:
        dataframe = dataframe[
            dataframe["alloy"].fillna("").str.contains(alloy, case=False, regex=False)
        ]

    record_id = str(query.get("record_id", "")).strip()
    if record_id:
        dataframe = dataframe[
            dataframe["unique_id"].fillna("").str.contains(
                record_id,
                case=False,
                regex=False,
            )
        ]

    structure = str(query.get("structure", "")).strip()
    if structure:
        dataframe = dataframe[
            dataframe["structure"].fillna("").str.contains(
                structure,
                case=False,
                regex=False,
            )
        ]

    complexity = str(query.get("complexity", "")).strip()
    if complexity:
        dataframe = dataframe[
            dataframe["complexity"].fillna("").str.contains(
                complexity,
                case=False,
                regex=False,
            )
        ]

    has_elastic = query.get("has_elastic")
    if isinstance(has_elastic, bool):
        dataframe = dataframe[dataframe["has_elastic"] == has_elastic]

    elements_present = query.get("elements_present", [])
    if isinstance(elements_present, str):
        elements_present = [elements_present]
    if isinstance(elements_present, list):
        for element in elements_present:
            normalized_element = str(element).strip().capitalize()
            if not normalized_element:
                continue
            column_name = f"{normalized_element}_present"
            if column_name in dataframe.columns:
                dataframe = dataframe[dataframe[column_name] == 1]

    numeric_filters = [
        ("atom_count", "atom_count_min", "atom_count_max"),
        ("bulk_modulus", "bulk_modulus_min", "bulk_modulus_max"),
        ("pugh_ratio", "pugh_ratio_min", "pugh_ratio_max"),
    ]
    for column_name, minimum_key, maximum_key in numeric_filters:
        minimum = query.get(minimum_key)
        maximum = query.get(maximum_key)
        if isinstance(minimum, int | float):
            dataframe = dataframe[dataframe[column_name].notna() & (dataframe[column_name] >= minimum)]
        if isinstance(maximum, int | float):
            dataframe = dataframe[dataframe[column_name].notna() & (dataframe[column_name] <= maximum)]

    limited_rows = dataframe.head(max(1, min(limit, 10))).to_dict("records")
    return [_build_dft_result_row(row) for row in limited_rows]
