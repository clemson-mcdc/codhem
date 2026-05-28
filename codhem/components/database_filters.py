import streamlit as st


PROPERTY_FILTERS = [
    {
        "key": "phase",
        "label": "Phase",
        "kind": "select",
    },
    {"key": "rho", "label": "ρ (g/cm3)", "kind": "range"},
    {"key": "elastic_modulus", "label": "E (GPa)", "kind": "range"},
    {"key": "sigma_at_23_c", "label": "σ (MPa) at 23 C", "kind": "range"},
    {"key": "sigma_at_1000_c", "label": "σ (MPa) at 1000 C", "kind": "range"},
    {"key": "sigma_at_1200_c", "label": "σ (MPa) at 1200 C", "kind": "range"},
    {"key": "shear_modulus", "label": "G (GPa)", "kind": "range"},
    {"key": "c11", "label": "C11 (GPa)", "kind": "range"},
    {"key": "ductility", "label": "Ductility [%]", "kind": "range"},
]


def _parse_float(raw_value):
    if raw_value is None:
        return None
    text = str(raw_value).strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _render_property_filter(filter_definition, key_prefix, phase_options):
    row_col_1, row_col_2, row_col_3 = st.columns(
        [1.5, 2.5, 1],
        vertical_alignment="center",
    )
    row_col_1.write(filter_definition["label"])

    if filter_definition["kind"] == "select":
        selected_value = row_col_2.selectbox(
            filter_definition["label"],
            [""] + phase_options,
            key=f"{key_prefix}-{filter_definition['label']}-value",
            label_visibility="collapsed",
        )
        is_active = row_col_3.toggle(
            "Active",
            value=False,
            key=f"{key_prefix}-{filter_definition['label']}-active",
            label_visibility="collapsed",
        )
        if is_active and selected_value:
            return selected_value
        return None
    else:
        range_col_1, range_col_2 = row_col_2.columns(2)
        minimum_value = range_col_1.text_input(
            "Min",
            key=f"{key_prefix}-{filter_definition['label']}-minimum",
            placeholder="Min",
        )
        maximum_value = range_col_2.text_input(
            "Max",
            key=f"{key_prefix}-{filter_definition['label']}-maximum",
            placeholder="Max",
        )
        is_active = row_col_3.toggle(
            "Active",
            value=False,
            key=f"{key_prefix}-{filter_definition['label']}-active",
            label_visibility="collapsed",
        )
        if not is_active:
            return None
        return {
            "minimum": _parse_float(minimum_value),
            "maximum": _parse_float(maximum_value),
        }


def render_database_filters(
    phase_options,
    selected_elements,
    key_prefix="database-filters",
):
    st.subheader("Database Filters")

    properties_col, composition_col = st.columns(2, gap="large")
    filter_state = {
        "phase": None,
        "property_ranges": {},
        "composition_ranges": {},
    }

    with properties_col:
        st.markdown("##### Filter by properties")
        with st.container(height=420, border=True):
            for filter_definition in PROPERTY_FILTERS:
                value = _render_property_filter(
                    filter_definition,
                    key_prefix,
                    phase_options,
                )
                if value is None:
                    continue
                if filter_definition["key"] == "phase":
                    filter_state["phase"] = value
                else:
                    filter_state["property_ranges"][filter_definition["key"]] = value

    with composition_col:
        st.markdown("##### Filter by composition (%)")
        with st.container(height=420, border=True):
            if not selected_elements:
                st.info("Select elements from the periodic table to add composition filters.")
            for element in selected_elements:
                row_col_1, row_col_2, row_col_3 = st.columns(
                    [1.5, 2.5, 1],
                    vertical_alignment="center",
                )
                row_col_1.write(element)
                range_col_1, range_col_2 = row_col_2.columns(2)
                minimum_value = range_col_1.text_input(
                    "Min",
                    key=f"{key_prefix}-{element}-composition-minimum",
                    placeholder="Min %",
                )
                maximum_value = range_col_2.text_input(
                    "Max",
                    key=f"{key_prefix}-{element}-composition-maximum",
                    placeholder="Max %",
                )
                is_active = row_col_3.toggle(
                    "Active",
                    value=False,
                    key=f"{key_prefix}-{element}-composition-active",
                    label_visibility="collapsed",
                )
                minimum = _parse_float(minimum_value)
                maximum = _parse_float(maximum_value)
                if is_active and (minimum is not None or maximum is not None):
                    filter_state["composition_ranges"][element] = {
                        "minimum": minimum,
                        "maximum": maximum,
                    }

    return filter_state
