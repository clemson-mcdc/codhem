from dataclasses import dataclass


@dataclass(frozen=True)
class OxygenVacancyBaderData:
    vacancy_nearest_neighbors: float | None = None
    by_element: dict[str, float] | None = None
    per_atom: dict[str, float] | None = None
    total_per_atom: float | None = None
    volume: float | None = None


@dataclass(frozen=True)
class OxygenVacancyVolumeData:
    vacancy: float | None = None
    perfect: float | None = None
    difference: float | None = None
    ratio: float | None = None


@dataclass(frozen=True)
class OxygenVacancyDisplacementData:
    initial: float | None = None
    final: float | None = None
    difference: float | None = None


@dataclass(frozen=True)
class OxygenVacancyRecord:
    system: str
    vacancy_position: int
    index: int | None = None
    defect_energy: float | None = None
    perfect_energy: float | None = None
    oxygen_vacancy_energy: float | None = None
    vacancy_formation_energy: float | None = None
    neighbor_composition: dict[str, int] | None = None
    bader: OxygenVacancyBaderData | None = None
    volume: OxygenVacancyVolumeData | None = None
    displacement: OxygenVacancyDisplacementData | None = None
