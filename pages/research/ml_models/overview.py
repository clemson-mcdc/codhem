import streamlit as st

from codhem.services.auth_service import require_registered_user

require_registered_user()


st.title("ML Models")
st.caption(
    'Choose a prediction model and provide an alloy composition to estimate its '
    'properties. The RHEA-DOS-E predictor returns electronic density of states at the '
    "Fermi level and Young's modulus. Open the model form below, or use Query using LLM "
    'to request a prediction in chat.'
)
if st.button("Query using LLM", icon=":material/neurology:", type="primary"):
    st.switch_page("pages/research/ml_models/llm.py")

with st.container(border=True):
    st.subheader("RHEA-DOS-E Predictor")
    st.write(
        "Predicts the electronic density of states at the Fermi level and "
        "Young's modulus for refractory high-entropy alloys."
    )
    if st.button("Open model", width="stretch", key="rhea-mpnn"):
        st.switch_page("pages/research/ml_models/rhea_mpnn.py")
