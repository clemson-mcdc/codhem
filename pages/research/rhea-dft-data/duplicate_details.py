import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

from codhem.components.periodic_table import ELEMENTS
from codhem.services.auth_service import require_registered_user


require_registered_user()

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="DFT CALCULATIONS DASHBOARD",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# LOAD CSS (UNIVERSAL FILE – SCOPED BELOW)
# =====================================================
def load_css():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, "styles.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# =====================================================
# PAGE WRAPPER (CSS SCOPE)
# =====================================================
st.markdown('<div class="composition-dashboard">', unsafe_allow_html=True)

# =====================================================
# TITLE
# =====================================================
st.title("⚛️ DFT Calculation Dashboard for High Entropy Alloys")
st.caption("Compositional Space Coverage (Composition Only)")

# =====================================================
# GET FILTERED DATA
# =====================================================
if "filtered_df" not in st.session_state:
    st.warning("No filtered data found.")
    st.stop()

df = st.session_state["filtered_df"].copy()
if df.empty:
    st.warning("Filtered dataset is empty.")
    st.stop()

# =====================================================
# ELEMENT DEFINITIONS
# =====================================================
elements = [element["symbol"] for element in ELEMENTS]

comp_cols = [f"{el}_comp" for el in elements if f"{el}_comp" in df.columns]

# keep only rows where at least 2 elements exist
df = df[df[comp_cols].sum(axis=1) > 0]


def compute_pca_coordinates(dataframe: pd.DataFrame) -> np.ndarray:
    matrix = dataframe.to_numpy(dtype=float)
    centered = matrix - matrix.mean(axis=0, keepdims=True)
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    components = vt[:2].T
    return centered @ components

# =====================================================
# ROW 1 — TERNARY + PCA
# =====================================================
col1, col2 = st.columns(2, gap="large")

# ------------------ TERNARY ------------------
with col1:
    st.subheader("🔺 Ternary Composition Plot")

    ternary_elements = st.multiselect(
        "Select 3 elements",
        options=[el for el in elements if f"{el}_comp" in df.columns],
        default=[el for el in elements if f"{el}_comp" in df.columns][:3],
        max_selections=3
    )

    if len(ternary_elements) == 3:
        a, b, c = ternary_elements
        tern_df = df[[f"{a}_comp", f"{b}_comp", f"{c}_comp"]].copy()
        tern_df.columns = [a, b, c]

        tern_df = tern_df[(tern_df.sum(axis=1) > 0)]

        fig_tern = px.scatter_ternary(
            tern_df,
            a=a, b=b, c=c,
            size_max=6,
            opacity=0.8
        )
        fig_tern.update_layout(height=420)
        st.plotly_chart(fig_tern, width="stretch")
    else:
        st.info("Select exactly 3 elements.")

# ------------------ PCA ------------------
with col2:
    st.subheader("📉 PCA of Composition Space")

    pca_df = df[comp_cols].fillna(0)
    coords = compute_pca_coordinates(pca_df)

    pca_plot_df = pd.DataFrame(coords, columns=["PC1", "PC2"])

    fig_pca = px.scatter(
        pca_plot_df,
        x="PC1",
        y="PC2",
        opacity=0.8
    )
    fig_pca.update_layout(height=420)
    st.plotly_chart(fig_pca, width="stretch")

# =====================================================
# ROW 2 — PARALLEL + PAIRWISE
# =====================================================
col3, col4 = st.columns(2, gap="large")

# ------------------ PARALLEL COORDINATES ------------------
with col3:
st.subheader("🧬 Parallel Coordinates (Composition)")

    fig_parallel = px.parallel_coordinates(
        df,
        dimensions=comp_cols,
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig_parallel.update_layout(height=450)
    st.plotly_chart(fig_parallel, width="stretch")

# ------------------ PAIRWISE ------------------
with col4:
st.subheader("🔁 Binary Composition Projection")

    el_x = st.selectbox("X-axis element", elements, index=0)
    el_y = st.selectbox("Y-axis element", elements, index=1)

    if f"{el_x}_comp" in df.columns and f"{el_y}_comp" in df.columns:
        fig_pair = px.scatter(
            df,
            x=f"{el_x}_comp",
            y=f"{el_y}_comp",
            opacity=0.8
        )
        fig_pair.update_layout(
            xaxis_title=f"{el_x} (%)",
            yaxis_title=f"{el_y} (%)",
            height=450
        )
        st.plotly_chart(fig_pair, width="stretch")
    else:
        st.info("Selected elements not present in dataset.")

# =====================================================
# CLOSE PAGE WRAPPER
# =====================================================
st.markdown('</div>', unsafe_allow_html=True)
