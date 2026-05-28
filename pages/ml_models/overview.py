import streamlit as st

from codhem.services.auth_service import require_registered_user

require_registered_user()


st.title("ML Models")
st.caption("Select a model to open its input and output page.")

with st.container(border=True):
    st.subheader("RHEA-DOS-E Predictor")
    st.write(
        "Predicts the electronic density of states at the Fermi level and "
        "Young's modulus for refractory high-entropy alloys."
    )
    if st.button("Open model", width="stretch", key="rhea-mpnn"):
        st.switch_page("pages/ml_models/rhea_mpnn.py")
