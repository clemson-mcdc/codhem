from dataclasses import dataclass


@dataclass(frozen=True)
class FilterCriteria:
    material: str = "All"
    instrument: str = "All"
    min_temperature: float = 0.0
    max_temperature: float = 300.0
