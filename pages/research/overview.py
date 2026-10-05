import streamlit as st

from codhem.services.auth_service import require_registered_user


require_registered_user()

st.title("Home")
st.caption(
    "MCDC research datasets and prediction models connect alloy electronic "
    "structure, elastic properties, and oxide vacancy behavior through "
    "interactive analysis and dedicated natural-language assistants."
)

st.divider()
st.subheader("RHEA DFT Data")
st.write(
    "The RHEA dataset contains density functional theory calculations for "
    "refractory high-entropy alloys, connecting composition and structure with "
    "electronic and elastic properties. Coverage summaries distinguish records "
    "with complete elastic data from those with missing values, while plots "
    "compare elemental occurrence, alloy complexity, moduli, Pugh ratio, and "
    "density of states at the Fermi level. Detailed views extend these comparisons "
    "to selected alloys, with composition-space analyses and available calculation "
    "files. A dedicated assistant searches calculation records using "
    "natural-language filters."
)

st.page_link(
    "pages/research/rhea-dft-data/overview.py",
    label="RHEA DFT Data",
    icon=":material/arrow_forward:",
)
st.divider()
st.subheader("HEO Vacancy Data")
st.write(
    "The HEO dataset describes oxygen-vacancy configurations across oxide "
    "systems, including vacancy formation energies, local neighbor compositions, "
    "Bader charge values, and volume and displacement changes. Configuration "
    "comparisons and formation-energy distributions show how vacancy properties "
    "vary within and across systems. A local-environment visualization presents "
    "the oxygen-centered octahedron and its neighboring elements. The dedicated "
    "assistant supports record searches by system, vacancy position, neighbor "
    "elements, and numeric property conditions."
)
st.page_link(
    "pages/research/oxygen_vacancy_data.py",
    label="HEO Vacancy Data",
    icon=":material/arrow_forward:",
)
st.divider()
st.subheader("ML Models")
st.write(
    "The model collection currently includes the RHEA-DOS-E predictor, which "
    "estimates electronic density of states at the Fermi level and Young's "
    "modulus for refractory high-entropy alloys. Trained on DFT data, the model "
    "uses alloy compositions in atomic percent to produce electronic and "
    "elastic-property predictions without a new DFT calculation. Predictions "
    "are available through both a dedicated model form and a conversational "
    "assistant connected to the same predictor."
)
st.page_link(
    "pages/research/ml_models/overview.py",
    label="ML Models",
    icon=":material/arrow_forward:",
)
