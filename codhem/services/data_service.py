from codhem.models.domain import ScientificRecord


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

