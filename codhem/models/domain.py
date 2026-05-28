from dataclasses import dataclass


@dataclass(frozen=True)
class ScientificRecord:
    dataset_id: str
    material: str
    temperature: float
    signal: float
    instrument: str


@dataclass(frozen=True)
class DatabaseStatistics:
    total_compositions: int
    total_dois: int
    element_distribution: list[dict[str, int | str]]
    phase_distribution: list[dict[str, int | str]]
    distinctive_composition_distribution: list[dict[str, int | str]]


@dataclass(frozen=True)
class DftCalculation:
    mongo_id: str
    unique_id: str
    user: str
    directory: str
    path: str
    alloy: str
    atom_count: int
    structure: str
    potcar: str
    lattice_params: dict[str, float | None]
    vol_per_atom: float | None
    local_lattice_distortion: float | None
    fermi_energy: float | None
    dos_at_fermi: dict[str, float | None]
    bonding_area: float | None
    antibonding_area: float | None
    d_band_center: float | None
    element_composition: dict[str, float]
    structure_counts: dict[str, int]
    data: dict[str, str | None]
    elastic_constants: dict[str, float | None]
    shear_modulus: dict[str, float | None]
    bulk_modulus: float | None
    youngs_modulus: dict[str, float | None]
    poisson_ratio: float | None
    pugh_ratio: float | None
