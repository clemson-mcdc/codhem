import streamlit as st

from codhem.models.filters import FilterCriteria


FILTER_STATE_KEY = "current_filters"


def get_current_filters():
    state = st.session_state.get(FILTER_STATE_KEY)
    if isinstance(state, FilterCriteria):
        return state
    default_filters = FilterCriteria()
    st.session_state[FILTER_STATE_KEY] = default_filters
    return default_filters


def set_current_filters(criteria: FilterCriteria):
    st.session_state[FILTER_STATE_KEY] = criteria
