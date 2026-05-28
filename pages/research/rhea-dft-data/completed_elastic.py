import streamlit as st
import os

from codhem.services.auth_service import require_registered_user
from codhem.services.dft_calculations_service import build_dft_calculations_dashboard_dataframe


require_registered_user()

st.set_page_config(
    page_title="Completed Elastic",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_css():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, "detail_styles.css")
    css_path = os.path.normpath(css_path)
    
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# =====================================================
# NUCLEAR CSS OVERRIDE FOR BUTTONS - ADD THIS SECTION
# =====================================================


st.title("🧪 DFT Calculations Dashboard")
st.caption("Structured database of Body-Centered Cubic (BCC) alloys")
st.header("✅ Elastic Tensor & DOS Available")

# =====================================================
# BACK BUTTON
# =====================================================
# =====================================================
# DATA LOADING AND FILTERING
# =====================================================
df = build_dft_calculations_dashboard_dataframe()
filtered_data = df[df["has_elastic"]].copy()
csv_data = filtered_data.to_csv(index=False).encode('utf-8')

col1, col2 = st.columns(2)

with col1:
    if st.button("← Back to Dashboard", key="back_button"):
        st.switch_page("pages/research/rhea-dft-data/overview.py")

with col2:
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name="Elastic_tensor_Dos.csv",
        mime="text/csv",
        key="download_csv"
    )


# =====================================================
# DATA DISPLAY
# =====================================================
st.dataframe(
    filtered_data,
    width="stretch",
    hide_index=True
)
