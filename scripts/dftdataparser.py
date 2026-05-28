import argparse
import csv
import json
import re
import shutil
import uuid
from pathlib import Path


def to_int(value):
    return int(float(value))


def to_float(value):
    if value == "":
        return None
    return float(value)


def source_data_paths(data_dir, unique_id):
    return {
        "contcar": data_dir / "CONTCAR" / f"CONTCAR_{unique_id}",
        "pdos": data_dir / "PDOS_USER.dat" / f"PDOS_USER_{unique_id}.dat",
        "tdos": data_dir / "TDOS.dat" / f"TDOS_{unique_id}.dat",
    }


def move_data_files(data_dir, source_unique_id, output_unique_id):
    source_paths = source_data_paths(data_dir, source_unique_id)
    destination_paths = {
        "contcar": data_dir / "contcar" / output_unique_id,
        "pdos": data_dir / "pdos" / output_unique_id,
        "tdos": data_dir / "tdos" / output_unique_id,
    }

    for path in destination_paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    for key, source_path in source_paths.items():
        if source_path.exists():
            shutil.move(str(source_path), str(destination_paths[key]))


def row_to_document(row, output_unique_id):
    element_composition = {}
    for column, raw_value in row.items():
        match = re.fullmatch(r"([A-Z][a-z]?)_comp", column)
        if not match:
            continue

        value = to_float(raw_value)
        if value != 0:
            element_composition[match.group(1).lower()] = value

    return {
        "unique_id": output_unique_id,
        "user": row["User"],
        "directory": row["Folder"],
        "path": row["Full_path"],
        "alloy": row["Alloy"],
        "atom_count": to_int(row["Total_atoms"]),
        "structure": row["Structure (By OVITO)"],
        "potcar": row["POTCAR_used"],
        "lattice_params": {
            "x": to_float(row["Lattice_parameter_x (Å)"]),
            "y": to_float(row["Lattice_parameter_y (Å)"]),
            "z": to_float(row["Lattice_parameter_z (Å)"]),
        },
        "vol_per_atom": to_float(row["Volumetric_lattice_parameter (Å)"]),
        "local_lattice_distortion": to_float(row["LLD (Å)"]),
        "fermi_energy": to_float(row["Fermi_energy (eV)"]),
        "dos_at_fermi": {
            "total": to_float(row["Nef (states/eV/atom)"]),
            "t2g": to_float(row["t2g_NEF (states/eV/atom)"]),
            "eg": to_float(row["eg_NEF (states/eV/atom)"]),
        },
        "bonding_area": to_float(row["Bonding_area (states·eV/atom)"]),
        "antibonding_area": to_float(row["Antibonding_area (states·eV/atom)"]),
        "d_band_center": to_float(row["D_band_center (eV)"]),
        "element_composition": element_composition,
        "structure_counts": {
            "bcc": to_int(row["Structure_individual_BCC"]),
            "fcc": to_int(row["Structure_individual_FCC"]),
            "hcp": to_int(row["Structure_individual_HCP"]),
        },
        "elastic_constants": {
            "c_11": to_float(row["C_11 [GPa]"]),
            "c_12": to_float(row["C_12 [GPa]"]),
            "c_13": to_float(row["C_13 [GPa]"]),
            "c_22": to_float(row["C_22 [GPa]"]),
            "c_23": to_float(row["C_23 [GPa]"]),
            "c_33": to_float(row["C_33 [GPa]"]),
            "c_44": to_float(row["C_44 [GPa]"]),
            "c_55": to_float(row["C_55 [GPa]"]),
            "c_66": to_float(row["C_66 [GPa]"]),
        },
        "shear_modulus": {
            "voigt": to_float(row["G_V [GPa]"]),
            "reuss": to_float(row["G_R [GPa]"]),
            "average": to_float(row["G [GPa]"]),
        },
        "bulk_modulus": to_float(row["B [GPa]"]),
        "youngs_modulus": {
            "e_100": to_float(row["E_100 [GPa]"]),
            "e_110": to_float(row["E_110 [GPa]"]),
            "e_111": to_float(row["E_111 [GPa]"]),
            "e_113": to_float(row["E_113 [GPa]"]),
            "e_331": to_float(row["E_331 [GPa]"]),
            "e_vrh": to_float(row["E_VRH [GPa]"]),
        },
        "poisson_ratio": to_float(row["Poisson's ratio []"]),
        "pugh_ratio": to_float(row["Pugh_Ratio"]),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--data-dir", required=True)
    args = parser.parse_args()

    input_csv = Path(args.input_csv)
    output_json = Path(args.output_json)
    data_dir = Path(args.data_dir)

    with input_csv.open(newline="", encoding="utf-8-sig") as infile:
        rows = list(csv.DictReader(infile))

    documents = []
    for row in rows:
        output_unique_id = str(uuid.uuid4())
        move_data_files(data_dir, row["Unique_ID"], output_unique_id)
        documents.append(row_to_document(row, output_unique_id))

    with output_json.open("w", encoding="utf-8") as outfile:
        json.dump(documents, outfile, indent=2)

    print(f"Wrote {len(documents)} records to {output_json}")


if __name__ == "__main__":
    main()
