import argparse
import csv
import json
import re
import uuid
from pathlib import Path


def to_float(value):
    if value == "":
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", value.replace("−", "-"))
    if not match:
        return None
    return float(match.group())


def to_int(value):
    if value == "":
        return None
    parsed = to_float(value)
    if parsed is None:
        return None
    return int(parsed)


def to_bool(value):
    if value == "":
        return None
    return bool(int(value))


def drop_empty(value):
    if isinstance(value, dict):
        cleaned = {
            key: drop_empty(child)
            for key, child in value.items()
            if drop_empty(child) is not None
        }
        return cleaned or None
    if isinstance(value, list):
        cleaned = [drop_empty(child) for child in value if drop_empty(child) is not None]
        return cleaned
    if value in ("", None):
        return None
    return value


def row_to_document(row):
    element_composition = {}
    for column, raw_value in row.items():
        match = re.fullmatch(r"atom_composition\.(.+)", column)
        if not match or raw_value == "":
            continue
        element_composition[match.group(1).lower()] = to_float(raw_value)

    document = {
        "type": row["type"],
        "unique_id": str(uuid.uuid4()),
        "doi": row["doi"],
        "created_at": row["CreatedAt"],
        "verified": to_bool(row["verified"]),
        "composition": row["Composition"] or row["composition"],
        "density": to_float(
            row.get("Density (g/cm3)")
            or row.get("Desnity (g/cm3)")
            or row.get("ρ (g/cm<sup>3</sup>)", "")
        ),
        "element_composition": element_composition,
        "phase_data": {
            "phase": row["Phase"] or None,
            "type_of_phase": row["Type of phase(s)"] or None,
            "types_of_phases": row["Type(s) of phase(s)"] or None,
            "types_of_phases_subscripted": (
                row["Type(s) of phase(s)_subscripted"] or None
            ),
        },
        "mechanical_properties": {
            "elastic_modulus": to_float(row["E (GPa)"]),
            "youngs_modulus": to_float(row["Young's modulus  (GPa)"]),
            "shear_modulus": to_float(row["G (GPa)"]),
            "c11": to_float(row["C11 (GPa)"]),
            "c12": to_float(row["C12 (GPa)"]),
            "c44": to_float(row["C44 (GPa)"]),
            "hardness_hv": to_float(row["Hardness (HV)"]),
            "hardness": to_float(row["Hardness (GPa)"]),
            "tensile_ys": to_float(row["Tensile YS (MPa)"]),
            "uts": to_float(row["UTS (MPa)"]),
            "sigma_at_23_c": to_float(row["σ(Mpa) at 23 C"]),
            "sigma_at_1000_c": to_float(row["σ(Mpa) at 1000 C"]),
            "sigma_at_1200_c": to_float(row["σ(Mpa) at 1200 C"]),
            "ductility": to_float(row["Ductility [%]"]),
            "fracture_toughness": to_float(
                row["fracture toughness (MPa*m<sup>1/2</sup>)"]
            ),
        },
        "test_data": {
            "type_of_test": row["Type of test"] or None,
            "testing_temperature": to_float(row["Testing temperature (K)"]),
            "grain_size": to_float(row["Grain size (um)"]),
        },
        "computed_properties": {
            "rmsad": to_float(row["RMSAD"]),
            "surface_energy": to_float(row["Surface energy (SURF)"]),
            "unstable_stacking_fault_energy": to_float(
                row["Unstable stacking fault energy (USFE)"]
            ),
        },
    }
    return drop_empty(document) or {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    input_csv = Path(args.input_csv)
    output_json = Path(args.output_json)

    with input_csv.open(newline="", encoding="utf-8-sig") as infile:
        rows = list(csv.DictReader(infile))

    documents = [row_to_document(row) for row in rows]

    with output_json.open("w", encoding="utf-8") as outfile:
        json.dump(documents, outfile, indent=2)

    print(f"Wrote {len(documents)} records to {output_json}")


if __name__ == "__main__":
    main()
