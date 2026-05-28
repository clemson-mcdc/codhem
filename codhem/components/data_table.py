import streamlit as st

from codhem.models.domain import ScientificRecord


def render_record_table(records: list[ScientificRecord]):
    table_rows = [
        {
            "Dataset": record.dataset_id,
            "Material": record.material,
            "Temperature": record.temperature,
            "Signal": record.signal,
            "Instrument": record.instrument,
        }
        for record in records
    ]
    st.dataframe(table_rows, width="stretch", hide_index=True)
