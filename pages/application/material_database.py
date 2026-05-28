import pandas as pd
import plotly.express as px
import streamlit as st

from codhem.components.database_filters import render_database_filters
from codhem.components.periodic_table import render_periodic_table
from codhem.services.auth_service import require_registered_user
from codhem.services.literature_data_service import (
    get_literature_elements,
    get_literature_phase_options,
    query_literature_data,
)


require_registered_user()

PLOT_AXIS_OPTIONS = [
    "ρ (g/cm3)",
    "E (GPa)",
    "σ (MPa) at 23 C",
    "G (GPa)",
    "C11 (GPa)",
    "Ductility [%]",
]


def toggle_selected_element(symbol):
    selected_elements = st.session_state.setdefault(
        "material_database_selected_elements",
        [],
    )
    if symbol in selected_elements:
        selected_elements.remove(symbol)
    else:
        selected_elements.append(symbol)


def classify_phase_bucket(value):
    phase_text = str(value or "").upper()
    if "FCC" in phase_text:
        return "FCC"
    if "BCC" in phase_text:
        return "BCC"
    return "Other"


st.title("COD'HEM Database")
st.caption(
    "Browse elements and use the periodic table as an entry point into the database."
)

available_elements = get_literature_elements()
phase_options = get_literature_phase_options()

render_periodic_table(
    toggle_selected_element,
    selected_symbols=st.session_state.get(
        "material_database_selected_elements",
        [],
    ),
    available_symbols=available_elements,
    key_prefix="material-database-periodic-table",
)

selected_elements = st.session_state.get("material_database_selected_elements", [])
if selected_elements:
    st.caption(f"Selected elements: {', '.join(selected_elements)}")
    if st.button("Clear selected elements", key="material-database-clear-elements"):
        st.session_state["material_database_selected_elements"] = []
        st.rerun()

st.divider()
filter_state = render_database_filters(
    phase_options=phase_options,
    selected_elements=selected_elements,
    key_prefix="material-database-filters",
)

results = query_literature_data(
    tuple(sorted(selected_elements)),
    filter_state["phase"],
    filter_state["property_ranges"],
    filter_state["composition_ranges"],
)

st.divider()
st.subheader("Database Results")
st.caption(f"{len(results)} records")
st.dataframe(results, width="stretch", hide_index=True)

st.divider()
st.subheader("Data Visualization")

plot_control_col_1, plot_control_col_2, plot_control_col_3 = st.columns(3)
with plot_control_col_1:
    x_axis = st.selectbox(
        "X axis",
        PLOT_AXIS_OPTIONS,
        key="material-database-plot-x-axis",
    )
with plot_control_col_2:
    y_axis = st.selectbox(
        "Y axis",
        PLOT_AXIS_OPTIONS,
        index=1,
        key="material-database-plot-y-axis",
    )
with plot_control_col_3:
    plot_phase = st.selectbox(
        "Phase",
        ["FCC", "BCC", "Other"],
        key="material-database-plot-phase",
    )

plot_results = results.copy()
if not plot_results.empty:
    plot_results["Phase Bucket"] = plot_results["Phase"].map(classify_phase_bucket)
    plot_results = plot_results[plot_results["Phase Bucket"] == plot_phase].copy()
    plot_results[x_axis] = pd.to_numeric(plot_results[x_axis], errors="coerce")
    plot_results[y_axis] = pd.to_numeric(plot_results[y_axis], errors="coerce")
    plot_results = plot_results.dropna(subset=[x_axis, y_axis])

if plot_results.empty:
    st.info("No data available for the selected plot settings.")
else:
    figure = px.scatter(
        plot_results,
        x=x_axis,
        y=y_axis,
        hover_data=["Composition", "DOI", "Phase"],
    )
    figure.update_layout(height=520)
    st.plotly_chart(figure, width="stretch")
