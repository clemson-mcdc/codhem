from codhem.models.filters import FilterCriteria


def validate_filter_range(criteria: FilterCriteria):
    return criteria.min_temperature <= criteria.max_temperature
