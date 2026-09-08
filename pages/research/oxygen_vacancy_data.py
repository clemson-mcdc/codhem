from collections import Counter

import numpy as np
import plotly.graph_objects as go
import py3Dmol
import streamlit as st
from plotly.subplots import make_subplots
from scipy.stats import gaussian_kde
from stmol import showmol

from codhem.services.auth_service import require_registered_user
from codhem.services.oxygen_vacancy_service import (
    get_average_vacancy_formation_energy,
    get_oxygen_vacancy_system_records,
    get_oxygen_vacancy_systems,
)

require_registered_user()

OXYGEN_COVALENT_RADIUS = 0.63
COVALENT_RADII = {
    "Mg": 1.39,
    "Cu": 1.12,
    "Ni": 1.10,
    "Co": 1.11,
    "Zn": 1.18,
}
OCTAHEDRAL_DIRECTIONS = [
    (1.0, 0.0, 0.0),
    (-1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, 0.0, 1.0),
    (0.0, 0.0, -1.0),
]
LATTICE_HALF_WIDTH = 5.0
LATTICE_LEVELS = (-5.0, -2.5, 0.0, 2.5, 5.0)
# TODO: derive this from Streamlit's active theme instead of hard-coding it.
PY3DMOL_BACKGROUND_COLOR = "#0e1117"
FALLBACK_SYSTEM_NEIGHBORS = {"MgO": ["Mg"] * 6}


def build_octahedral_xyz(neighbors):
    atoms = ["O 0.0 0.0 0.0"]
    atoms.extend(
        f"{element} {x * bond_length:.2f} {y * bond_length:.2f} {z * bond_length:.2f}"
        for element, (x, y, z) in zip(neighbors, OCTAHEDRAL_DIRECTIONS)
        for bond_length in (OXYGEN_COVALENT_RADIUS + COVALENT_RADII[element],)
    )
    return f"{len(atoms)}\nOxygen-centered octahedron\n" + "\n".join(atoms)


def build_lattice_xyz(neighbors):
    atoms = []
    atom_number = 1
    remaining_neighbor_number = 0

    for x_index, x in enumerate(LATTICE_LEVELS, start=1):
        for y_index, y in enumerate(LATTICE_LEVELS, start=1):
            for z_index, z in enumerate(LATTICE_LEVELS, start=1):
                if atom_number % 2 == 1:
                    element = "O"
                elif x_index == 4 and y_index == 3 and z_index == 3:
                    element = neighbors[0]
                elif x_index == 2 and y_index == 3 and z_index == 3:
                    element = neighbors[1]
                elif x_index == 3 and y_index == 4 and z_index == 3:
                    element = neighbors[2]
                elif x_index == 3 and y_index == 2 and z_index == 3:
                    element = neighbors[3]
                elif x_index == 3 and y_index == 3 and z_index == 4:
                    element = neighbors[4]
                elif x_index == 3 and y_index == 3 and z_index == 2:
                    element = neighbors[5]
                elif remaining_neighbor_number == 0:
                    element = neighbors[0]
                elif remaining_neighbor_number == 1:
                    element = neighbors[1]
                elif remaining_neighbor_number == 2:
                    element = neighbors[2]
                elif remaining_neighbor_number == 3:
                    element = neighbors[3]
                elif remaining_neighbor_number == 4:
                    element = neighbors[4]
                else:
                    element = neighbors[5]

                if atom_number % 2 == 0:
                    remaining_neighbor_number = (remaining_neighbor_number + 1) % 6
                atom_number += 1
                atoms.append(f"{element} {x:.2f} {y:.2f} {z:.2f}")

    return f"{len(atoms)}\nEnvironment\n" + "\n".join(atoms)


def build_composition_chart(neighbors):
    composition = Counter(neighbors)
    elements = sorted(composition)
    percentages = [composition[element] / len(neighbors) * 100 for element in elements]
    background_color = st.get_option("theme.backgroundColor") or "rgba(0, 0, 0, 0)"

    figure = go.Figure(
        go.Scatterpolar(
            r=percentages + [percentages[0]],
            theta=elements + [elements[0]],
            fill="toself",
            name="Neighbor composition",
            hovertemplate="%{theta}: %{r:.1f}%<extra></extra>",
        )
    )
    figure.update_layout(
        polar={
            "bgcolor": background_color,
            "radialaxis": {"visible": True, "range": [0, 100], "ticksuffix": "%"},
            "angularaxis": {"direction": "clockwise"},
        },
        paper_bgcolor=background_color,
        plot_bgcolor=background_color,
        showlegend=False,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        height=500,
    )
    return figure


def build_neighbors_from_record(record):
    if not record.neighbor_composition:
        return FALLBACK_SYSTEM_NEIGHBORS.get(record.system, [])

    neighbors = []
    for element, count in sorted((record.neighbor_composition or {}).items()):
        neighbors.extend([element] * count)
    return neighbors


def build_system_configuration_chart(system_records):
    elements = sorted(
        {
            element
            for record in system_records
            for element in (record.neighbor_composition or {})
        }
    )
    configurations = list(range(1, len(system_records) + 1))
    figure = make_subplots(specs=[[{"secondary_y": True}]])

    for element in elements:
        figure.add_trace(
            go.Bar(
                x=configurations,
                y=[
                    (record.neighbor_composition or {}).get(element, 0)
                    for record in system_records
                ],
                name=element,
            ),
            secondary_y=False,
        )

    formation_energies = [record.vacancy_formation_energy for record in system_records]
    if any(value is not None for value in formation_energies):
        figure.add_trace(
            go.Scatter(
                x=configurations,
                y=formation_energies,
                name="Vacancy formation energy",
                mode="lines+markers",
                marker={"symbol": "circle", "size": 9},
                line={"dash": "dot"},
                connectgaps=False,
            ),
            secondary_y=False,
        )

    tbc_values = [
        record.bader.vacancy_nearest_neighbors if record.bader else None
        for record in system_records
    ]
    if any(value is not None for value in tbc_values):
        figure.add_trace(
            go.Scatter(
                x=configurations,
                y=tbc_values,
                name="TBC",
                mode="lines+markers",
                marker={"symbol": "square", "size": 9},
                line={"dash": "dash"},
                connectgaps=False,
            ),
            secondary_y=True,
        )

    figure.update_layout(
        barmode="stack",
        height=500,
        margin={"l": 20, "r": 20, "t": 40, "b": 50},
        legend={"orientation": "h", "y": 1.12},
        hovermode="x unified",
    )
    figure.update_xaxes(title_text="Configurations", dtick=1)
    figure.update_yaxes(title_text="E<sub>vf</sub> [eV]", secondary_y=False)
    figure.update_yaxes(
        title_text="TBC [e]",
        secondary_y=True,
        showgrid=False,
        showline=True,
        side="right",
    )
    return figure


def build_vfe_density_chart(system_records_by_system):
    values_by_system = {
        system: np.array(
            [
                record.vacancy_formation_energy
                for record in records
                if record.vacancy_formation_energy is not None
            ]
        )
        for system, records in system_records_by_system.items()
    }
    value_min = 0.0
    value_max = float(np.concatenate(list(values_by_system.values())).max())
    plot_max = max(value_max * 1.25, 0.5)
    x_values = np.linspace(value_min, plot_max, 300)
    figure = go.Figure()

    for system, values in values_by_system.items():
        if len(values) > 1 and np.std(values) > 1e-9:
            density = gaussian_kde(values)(x_values)
        else:
            standard_deviation = 0.15
            density = np.exp(
                -0.5 * ((x_values - values.mean()) / standard_deviation) ** 2
            ) / (standard_deviation * np.sqrt(2 * np.pi))
        figure.add_trace(
            go.Scatter(
                x=x_values,
                y=density,
                mode="lines",
                name=system,
                line={"width": 4},
            )
        )

    figure.update_layout(
        height=500,
        margin={"l": 20, "r": 20, "t": 40, "b": 50},
        legend={"orientation": "h", "y": 1.12},
        hovermode="x unified",
    )
    figure.update_xaxes(
        title_text="E<sub>vf</sub> [eV]",
        range=[0, plot_max],
    )
    figure.update_yaxes(title_text="Probability density")
    return figure


def render_molecule(neighbors):
    view = py3Dmol.view(width=500, height=500)
    view.setBackgroundColor(PY3DMOL_BACKGROUND_COLOR)
    view.addModel(build_octahedral_xyz(neighbors), "xyz")
    view.setStyle({"stick": {"radius": 0.05}, "sphere": {"scale": 0.35}})
    view.setStyle({"elem": "O"}, {"stick": {"radius": 0.05}, "sphere": {"scale": 0.5}})
    for atom_index, element in enumerate(["O", *neighbors]):
        view.addLabel(
            element,
            {
                "backgroundOpacity": 0,
                "alignment": "center",
            },
            {"index": atom_index},
        )
    view.zoomTo()
    showmol(view, height=500, width=700)


def render_lattice(neighbors):
    view = py3Dmol.view(width=500, height=500)
    view.setBackgroundColor(PY3DMOL_BACKGROUND_COLOR)
    view.addModel(build_lattice_xyz(neighbors), "xyz")
    view.setStyle({}, {"sphere": {"scale": 0.5}})
    view.setStyle({"elem": "O"}, {"sphere": {"scale": 0.25}})
    view.addBox(
        {
            "center": {"x": 0, "y": 0, "z": 0},
            "dimensions": {
                "w": 2 * LATTICE_HALF_WIDTH,
                "h": 2 * LATTICE_HALF_WIDTH,
                "d": 2 * LATTICE_HALF_WIDTH,
            },
            "wireframe": True,
            "color": "#888888",
            "opacity": 0.35,
        }
    )
    view.zoomTo()
    showmol(view, height=500, width=1100)


st.title("Oxygen Vacancy Data")
st.caption(
    "Explore an oxygen-centered octahedral environment and its neighbor composition."
)

systems = get_oxygen_vacancy_systems()
if not systems:
    st.info("No oxygen-vacancy systems are available.")
    st.stop()

st.subheader("System")
selected_system = st.selectbox(
    "Select a system to show the available configurations of the system below.",
    systems,
    index=0,
    key="oxygen-vacancy-system",
)
records = get_oxygen_vacancy_system_records(selected_system)

st.subheader("Matching oxygen-vacancy records")
if not records:
    st.info("No records match the selected six-neighbor composition.")
else:
    st.caption("Select a configuration to display the corresponding charts below.")
    table_key = "oxygen-vacancy-records"
    table_state = st.session_state.get(table_key)
    selected_rows = []
    if table_state is not None:
        selection = getattr(table_state, "selection", None)
        if selection is None and hasattr(table_state, "get"):
            selection = table_state.get("selection", {})
        selected_rows = getattr(selection, "rows", None) or (
            selection.get("rows", []) if hasattr(selection, "get") else []
        )

    selected_system = (
        records[selected_rows[0]].system
        if selected_rows and selected_rows[0] < len(records)
        else records[0].system
    )
    system_records = (
        get_oxygen_vacancy_system_records(selected_system) if selected_system else []
    )
    system_average_formation_energy = get_average_vacancy_formation_energy(
        system_records
    )

    metric_column, count_column = st.columns(2)
    metric_column.metric(
        "Average $E_{vf}$ of the system",
        f"{system_average_formation_energy:.3f} eV"
        if system_average_formation_energy is not None
        else "N/A",
    )
    count_column.metric("Matching records", len(records))

    table_rows = [
        {
            "System": record.system,
            "Neighbor composition": record.neighbor_composition,
            "Vacancy position": record.vacancy_position,
            "Index": record.index,
            "VFE (eV)": record.vacancy_formation_energy,
            "Defect energy (eV)": record.defect_energy,
            "Oxygen vacancy energy (eV)": record.oxygen_vacancy_energy,
            "Bader charged": (
                record.bader.vacancy_nearest_neighbors if record.bader else None
            ),
            "Volume ratio": record.volume.ratio if record.volume else None,
            "Final displacement": (
                record.displacement.final if record.displacement else None
            ),
        }
        for record in records
    ]
    table_event = st.dataframe(
        table_rows,
        width="stretch",
        hide_index=True,
        column_config={
            "Index": None,
            "Defect energy (eV)": None,
            "Oxygen vacancy energy (eV)": None,
            "Volume ratio": None,
            "Final displacement": None,
        },
        key=table_key,
        on_select="rerun",
        selection_mode="single-row",
    )

    selected_rows = table_event.selection.rows
    selected_row = (
        selected_rows[0] if selected_rows and selected_rows[0] < len(records) else 0
    )
    selected_record = records[selected_row]
    selected_system = selected_record.system
    system_records = get_oxygen_vacancy_system_records(selected_system)

    selected_neighbors = build_neighbors_from_record(selected_record)
    if len(selected_neighbors) == 6:
        view_column, composition_column = st.columns(2)
        with view_column:
            st.markdown("**Environment**")
            show_octahedral = st.toggle(
                "Octahedral",
                value=False,
                key="oxygen-vacancy-show-octahedral",
            )
            if show_octahedral:
                render_molecule(selected_neighbors)
            else:
                render_lattice(selected_neighbors)

        with composition_column:
            st.markdown("**Neighbor composition**")
            st.plotly_chart(
                build_composition_chart(selected_neighbors),
                width="stretch",
            )

    st.markdown("**Configuration chart**")
    st.plotly_chart(
        build_system_configuration_chart(system_records),
        width="stretch",
    )

    st.markdown("**Vacancy formation energy distribution**")
    st.plotly_chart(
        build_vfe_density_chart({selected_system: system_records}),
        width="stretch",
    )
