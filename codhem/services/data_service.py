from codhem.models.domain import DatabaseStatistics, ScientificRecord


def build_plot_points(records: list[ScientificRecord]):
    return [
        {
            "dataset_id": record.dataset_id,
            "material": record.material,
            "temperature": record.temperature,
            "signal": record.signal,
        }
        for record in records
    ]


def get_database_statistics():
    return DatabaseStatistics(
        total_compositions=1284,
        total_dois=372,
        element_distribution=[
            {"label": "Fe", "count": 320},
            {"label": "Ni", "count": 275},
            {"label": "Co", "count": 240},
            {"label": "Cr", "count": 210},
            {"label": "Mn", "count": 180},
        ],
        phase_distribution=[
            {"label": "BCC", "count": 410},
            {"label": "FCC", "count": 365},
            {"label": "B2", "count": 205},
            {"label": "HCP", "count": 164},
            {"label": "Mixed", "count": 140},
        ],
        distinctive_composition_distribution=[
            {"label": "Fe", "count": 138},
            {"label": "Ni", "count": 124},
            {"label": "Cr", "count": 116},
            {"label": "Co", "count": 102},
            {"label": "Al", "count": 95},
            {"label": "Mn", "count": 88},
            {"label": "Ti", "count": 72},
        ],
    )
