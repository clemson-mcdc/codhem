import streamlit as st

from codhem.services.auth_service import require_registered_user


require_registered_user()

st.title("MCDC Research")
st.caption("Research dashboards and analyses developed by MCDC members.")

st.divider()
st.subheader("Member Dashboards")
st.write(
    "Each member dashboard presents a focused research workflow, calculation set, or analysis view."
)

st.page_link(
    "pages/research/rhea-dft-data/overview.py",
    label="RHEA DFT Data",
    icon=":material/arrow_forward:",
)
