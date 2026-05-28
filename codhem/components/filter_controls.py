import streamlit as st

from codhem.models.filters import FilterCriteria


def render_filter_controls(current_filters: FilterCriteria):
    with st.form("filter-controls"):
        left_col, right_col = st.columns(2)
        with left_col:
            material = st.selectbox(
                "Material",
                options=["All", "Copper", "Graphene", "Silicon"],
                index=["All", "Copper", "Graphene", "Silicon"].index(current_filters.material),
            )
            min_temperature = st.number_input(
                "Minimum temperature",
                value=float(current_filters.min_temperature),
            )
        with right_col:
            instrument = st.selectbox(
                "Instrument",
                options=["All", "Spectrometer", "Microscope", "Probe Station"],
                index=["All", "Spectrometer", "Microscope", "Probe Station"].index(
                    current_filters.instrument
                ),
            )
            max_temperature = st.number_input(
                "Maximum temperature",
                value=float(current_filters.max_temperature),
            )

        submitted = st.form_submit_button("Fetch data", width="stretch")

    if not submitted:
        return None

    return {
        "material": material,
        "instrument": instrument,
        "min_temperature": float(min_temperature),
        "max_temperature": float(max_temperature),
    }
