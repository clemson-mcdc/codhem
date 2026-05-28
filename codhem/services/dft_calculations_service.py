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
