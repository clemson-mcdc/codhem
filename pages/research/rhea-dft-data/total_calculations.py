import streamlit as st
import os

from codhem.services.auth_service import require_registered_user
from codhem.services.dft_calculations_service import build_dft_calculations_dashboard_dataframe


require_registered_user()

st.set_page_config(
    page_title="Total Calculations",
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

st.title("🧪 DFT Calculations Dashboard")
st.caption("Structured database of Body-Centered Cubic (BCC) alloys")
st.header("🧮 Total Calculations")

# =====================================================
# LOAD DATA
# =====================================================
df = build_dft_calculations_dashboard_dataframe()
csv_data = df.to_csv(index=False).encode('utf-8')

# =====================================================
# BUTTONS
# =====================================================
col1, col2 = st.columns(2)

with col1:
    if st.button("← Back to Dashboard", key="back_button"):
        st.switch_page("pages/research/rhea-dft-data/overview.py")

with col2:
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name="total_calculations.csv",
        mime="text/csv",
        key="download_csv"
    )

# =====================================================
# DATA DISPLAY
# =====================================================
st.dataframe(
    df,
    width="stretch",
)
