import streamlit as st
import pandas as pd
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
# LOAD CSS (same file, no changes)
# =====================================================
def load_css():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, "styles.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# =====================================================
# TITLE (EXACT SAME)
# =====================================================
st.title("⚛️ DFT Calculation Dashboard for High Entropy Alloys ")
st.caption("A Structured Computational Repository of Alloy Properties")

# =====================================================
# GET FILTERED DATA FROM SESSION
# =====================================================
if "filtered_df" not in st.session_state:
    st.warning("No filtered data found. Please go back and apply filters.")
    st.stop()

filtered_df = st.session_state["filtered_df"].copy()

if filtered_df.empty:
    st.warning("Filtered dataset is empty.")
    st.stop()

# =====================================================
# ELEMENT DEFINITIONS (same as main app)
# =====================================================
elements = [element["symbol"] for element in ELEMENTS]
present_cols = [f"{el}_present" for el in elements]

elastic_completed_filtered = filtered_df["has_elastic"]




























# # =====================================================
# # ALLOY COMPOSITION METRICS - 4 COLUMNS
# # =====================================================

# # Function to get unique element combinations in filtered dataset
# def get_unique_element_combinations(df):
#     combinations = {}
#     for idx, row in df.iterrows():
#         # Get elements present in this alloy
#         present_elements = []
#         for el in elements:
#             if row.get(f"{el}_present", 0) == 1:
#                 present_elements.append(el)
        
#         # Create a sorted string key for the combination
#         combo_key = " + ".join(sorted(present_elements))
#         if combo_key not in combinations:
#             combinations[combo_key] = 0
#         combinations[combo_key] += 1
    
#     return combinations

# # =====================================================
# # ALLOY COMPOSITION CARDS WITH SCROLLING
# # =====================================================
# # ALLOY COMPOSITION CARDS WITH SCROLLING
# # =====================================================

# unique_combinations = get_unique_element_combinations(filtered_df)

# # Display heading
# st.markdown('<h3>🧪 Alloy Compositions in Filtered Dataset</h3>', unsafe_allow_html=True)

# # Convert dict to list
# alloy_combinations = list(unique_combinations.items())

# # Generate all the card HTML first - using single line strings
# alloy_cards_html = ""
# for combo, count in alloy_combinations:
#     # Truncate display names
#     if len(combo) > 20:
#         display_name = combo[:17] + "..."
#     else:
#         display_name = combo
    
#     # Full name for tooltip
#     tooltip_name = combo[:50] + "..." if len(combo) > 50 else combo
    
#     # Create single-line HTML without newlines
#     alloy_cards_html += f'<div class="alloy-scroll-card" title="Full composition: {combo}"><div class="alloy-scroll-card-title">🧮 {display_name}</div><div class="alloy-scroll-card-value">{count}</div></div>'

# # Create the HTML structure
# alloy_scroll_html = f'<div class="alloy-scroll-container">{alloy_cards_html}</div>'

# # Add hint if there are many alloys
# if len(alloy_combinations) > 8:
#     alloy_scroll_html += '<p class="alloy-scroll-hint">Scroll to see more alloys ↓</p>'

# # Display everything
# st.markdown(alloy_scroll_html, unsafe_allow_html=True)




# =====================================================
# ADDITIONAL STATISTICS SECTION
# =====================================================

st.write("")
st.subheader("📈 Dataset Statistics")
st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    # Average number of elements per alloy
    avg_elements = filtered_df[present_cols].sum(axis=1).mean()
    st.markdown(
        f"""
        <div class="details-stat-card">
            <div class="details-stat-label">Average Elements per Alloy</div>
            <div class="details-stat-value">{avg_elements:.1f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    # Most common complexity
    def classify_complexity(row):
        n = int(row[present_cols].fillna(0).sum())
        return ["Pure","Binary","Ternary","Quaternary","Quinary"][n-1] if 1 <= n <= 5 else ">5 elements"
    
    most_common_complexity = filtered_df["complexity"].mode().iloc[0] if not filtered_df["complexity"].mode().empty else "N/A"
    st.markdown(
        f"""
        <div class="details-stat-card">
            <div class="details-stat-label">Most Common Complexity</div>
            <div class="details-stat-value">{most_common_complexity}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    # Completion percentage
    elastic_completed_filtered_count = elastic_completed_filtered.sum()
    total_filtered = len(filtered_df)
    completion_pct = (elastic_completed_filtered_count / total_filtered * 100) if total_filtered > 0 else 0
    st.markdown(
        f"""
        <div class="details-stat-card">
            <div class="details-stat-label">Elastic Completion Rate</div>
            <div class="details-stat-value">{completion_pct:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )



st.write("")






































# ---------------------------
# INTERACTIVE PLOTTING - SCATTER PLOT WITH CUSTOMIZATION
# ---------------------------





st.subheader("📊 Interactive Plotting Section")
st.write("")








import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit.components.v1 import html as st_html
from scipy.interpolate import interp1d
import re

# ---------------------------
# Helpers and small config
# ---------------------------
def get_plot_height_for_mode(style_mode: str) -> int:
    if style_mode == "By User":
        return 830
    if style_mode == "By Complexity":
        return 740
    if style_mode == "By Family":
        return 930
    return 900

elements = [
    "W","Mo","Ta","Nb","V","Cr","Fe","Li","K","Rb","Cs","Ba","Ra","Ca","Sr",
    "Rh","Ir","Ni","Pd","Pt","Cu","Ag","Au","Al","Ne","Ar","Kr","Xe",
    "Be","Mg","Sc","Y","Ti","Zr","Hf","Tc","Re","Ru","Os","Co","Zn","Cd","He"
]
present_cols = [f"{el}_present" for el in elements]

MARKER_OPTIONS = ["circle","square","diamond","triangle-up","cross","x","star"]
# Use a palette that contains good contrast — Plotly qualitative palettes combined
DEFAULT_COLORS = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Light24
LINE_STYLE_OPTIONS = {
    "No line": None,
    "--- line": "solid",
    "-.-.- line": "dashdot",
    "... line": "dot",
    "-- -- line": "dash",
    "----  ---- line": "longdash",
    "---- . ---- line": "longdashdot",
}

HEATMAP_SCALE_OPTIONS = {
    "Viridis": px.colors.sequential.Viridis,
    "Plasma": px.colors.sequential.Plasma,
    "Inferno": px.colors.sequential.Inferno,
    "Magma": px.colors.sequential.Magma,
    "Cividis": px.colors.sequential.Cividis,
    "Turbo": px.colors.sequential.Turbo,
    "Jet": px.colors.sequential.Jet,
    "RdBu": px.colors.diverging.RdBu,
    "Spectral": px.colors.diverging.Spectral,
    "Portland": px.colors.diverging.Portland,
    "Picnic": px.colors.diverging.Picnic,
    "Plotly3": px.colors.sequential.Plotly3,
}

def color_with_alpha(color_value, alpha):
    color_str = str(color_value).strip()
    if color_str.startswith("#") and len(color_str) == 7:
        r = int(color_str[1:3], 16)
        g = int(color_str[3:5], 16)
        b = int(color_str[5:7], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    return color_str

DOWNLOAD_BASE_WIDTH = 1200
DOWNLOAD_BASE_HEIGHT = 900
DOWNLOAD_ASPECT_RATIO = DOWNLOAD_BASE_WIDTH / DOWNLOAD_BASE_HEIGHT

def sync_download_from_width():
    width_val = int(st.session_state.get("scatter_download_width", DOWNLOAD_BASE_WIDTH))
    st.session_state["scatter_download_height"] = max(300, int(round(width_val / DOWNLOAD_ASPECT_RATIO)))
    st.session_state["scatter_download_scale"] = round(width_val / DOWNLOAD_BASE_WIDTH, 3)

def sync_download_from_height():
    height_val = int(st.session_state.get("scatter_download_height", DOWNLOAD_BASE_HEIGHT))
    st.session_state["scatter_download_width"] = max(400, int(round(height_val * DOWNLOAD_ASPECT_RATIO)))
    st.session_state["scatter_download_scale"] = round(height_val / DOWNLOAD_BASE_HEIGHT, 3)

def sync_download_from_scale():
    scale_val = float(st.session_state.get("scatter_download_scale", 1.0))
    st.session_state["scatter_download_width"] = max(400, int(round(DOWNLOAD_BASE_WIDTH * scale_val)))
    st.session_state["scatter_download_height"] = max(300, int(round(DOWNLOAD_BASE_HEIGHT * scale_val)))

# ---------- complexity / family helpers ----------
def classify_complexity(row):
    n = 0
    for c in present_cols:
        if c in row.index:
            try:
                vv = int(float(row[c]))
            except Exception:
                vv = 1 if pd.notna(row[c]) and str(row[c]).strip() not in ["0","0.0","False","false",""] else 0
            if vv:
                n += 1
    if n == 0:
        return "None"
    return ["Pure","Binary","Ternary","Quaternary","Quinary"][n-1] if 1 <= n <= 5 else ">5 elements"

def make_family_key(row):
    present = []
    for el in elements:
        col = f"{el}_present"
        if col in row.index:
            try:
                vv = int(float(row[col]))
            except Exception:
                vv = 1 if pd.notna(row[col]) and str(row[col]).strip() not in ["0","0.0","False","false",""] else 0
            if vv:
                present.append(el)
    if len(present) == 0:
        return ""
    return "-".join(sorted(present))


# ---------------------------
# DATA PREP - expect `filtered_df` to exist in environment
# ---------------------------
df_plot = filtered_df.copy()
df_plot["dos_at_fermi_total"] = df_plot["dos_at_fermi"].apply(
    lambda values: values.get("total") if isinstance(values, dict) else None
)
df_plot["shear_modulus_average"] = df_plot["shear_modulus"].apply(
    lambda values: values.get("average") if isinstance(values, dict) else None
)
df_plot["youngs_modulus_e_vrh"] = df_plot["youngs_modulus"].apply(
    lambda values: values.get("e_vrh") if isinstance(values, dict) else None
)

for c in present_cols:
    if c not in df_plot.columns:
        df_plot[c] = 0

if "FamilyKey" not in df_plot.columns:
    df_plot["FamilyKey"] = df_plot.apply(make_family_key, axis=1)

# Build list of numeric columns for plotting choices
requested_plot_props = [
    "vol_per_atom",
    "local_lattice_distortion",
    "bonding_area",
    "antibonding_area",
    "shear_modulus_average", "bulk_modulus",
    "youngs_modulus_e_vrh",
    "poisson_ratio", "pugh_ratio", "fermi_energy", "dos_at_fermi_total", "inv_pugh"
]
numeric_cols = []
for col in df_plot.columns:
    coerced = pd.to_numeric(df_plot[col], errors="coerce")
    if coerced.notna().sum() > 0:
        numeric_cols.append(col)
all_plot_columns = []
for c in requested_plot_props + numeric_cols:
    if c in df_plot.columns and c not in all_plot_columns:
        all_plot_columns.append(c)


# ---------------------------
# Autoscale helpers
# ---------------------------
def autoscale_axis(series, expand_factor=1.3):
    if series is None or series.empty:
        return 0.0, 1.0
    vmin = float(series.min())
    vmax = float(series.max())
    if vmin == vmax:
        pad = abs(vmin) * 0.05 + 1e-6
        return vmin - pad, vmax + pad
    center = 0.5 * (vmin + vmax)
    half_span = 0.5 * (vmax - vmin) * expand_factor
    return center - half_span, center + half_span

def autoscale_axis_asymmetric(series, left_factor=1.1, right_factor=1.6):
    if series is None or series.empty:
        return 0.0, 1.0
    vmin = float(series.min())
    vmax = float(series.max())
    if vmin == vmax:
        pad = abs(vmin) * 0.05 + 1e-6
        return vmin - pad, vmax + pad
    center = 0.5 * (vmin + vmax)
    base_half_span = 0.5 * (vmax - vmin)
    left_half = base_half_span * left_factor
    right_half = base_half_span * right_factor
    xmin = center - left_half
    xmax = center + right_half
    return xmin, xmax


# ---------------------------
# UI layout placeholders
# ---------------------------
col_plot, col_controls = st.columns([1.2, 1])
dos_placeholder = col_plot.empty()
scatter_placeholder = col_plot.empty()

# ---------------------------
# Controls
# ---------------------------
with col_controls:
    st.markdown('<div class="controls-section">', unsafe_allow_html=True)

    # Row 1: axis selectors
    r1c1, r1c2 = st.columns([1,1])
    with r1c1:
        x_col = st.selectbox("X axis", all_plot_columns, index=0, key="scatter_x")
    with r1c2:
        y_col = st.selectbox("Y axis", all_plot_columns, index=1 if len(all_plot_columns) > 1 else 0, key="scatter_y")

    # Row 2: users & complexities filters (multiselects)
    r2c1, r2c2 = st.columns([1,1])
    with r2c1:
        users = sorted(df_plot["user"].dropna().unique())
        selected_users = st.multiselect("Choose users", users, default=users, key="scatter_users")
    with r2c2:
        complexities = sorted(df_plot["complexity"].dropna().unique())
        selected_complexities = st.multiselect("Filter complexities", complexities, default=complexities, key="scatter_complexities")

    # Row 3: Lock Axis Scaling, Plot Alloy Names, Show other Alloys (33% each)
    r3c1, r3c2, r3c3, r3c4 = st.columns([1,1,1,1], gap="small")
    with r3c1:
        lock_axes = st.checkbox("Lock Axis Scaling", value=False, key="lock_axes_limits")
    with r3c2:
        plot_alloy_names = st.checkbox("Plot Alloy Names", value=False, key="plot_alloy_names")
    with r3c3:
        show_other_alloys = st.checkbox("Show other Alloys", value=False, key="show_other_alloys")
    with r3c4:
        add_marker_border = st.checkbox("Add marker border", value=False, key="scatter_add_marker_border")

    # Filter the df according to the user/compexity selections
    df_filtered_scatter = df_plot.copy()
    if selected_users and len(selected_users) > 0:
        df_filtered_scatter = df_filtered_scatter[df_filtered_scatter["user"].isin(selected_users)]
    if selected_complexities and len(selected_complexities) > 0:
        df_filtered_scatter = df_filtered_scatter[df_filtered_scatter["complexity"].isin(selected_complexities)]

    # Convert axis columns to numeric and drop NaNs
    df_filtered_scatter[x_col] = pd.to_numeric(df_filtered_scatter[x_col], errors="coerce")
    df_filtered_scatter[y_col] = pd.to_numeric(df_filtered_scatter[y_col], errors="coerce")
    df_filtered_scatter = df_filtered_scatter.dropna(subset=[x_col, y_col])

    # AUTOSCALE: compute defaults then possibly restrict if By Family & show_other_alloys==False
    a_xmin, a_xmax = autoscale_axis_asymmetric(df_filtered_scatter[x_col], left_factor=1.1, right_factor=1.6)
    a_ymin, a_ymax = autoscale_axis(df_filtered_scatter[y_col], expand_factor=1.1)

    # Detect current styling mode from session (widget may be set later; safe fallback)
    current_style_mode = st.session_state.get("scatter_styling_mode", None)

    if current_style_mode == "By Family" and (not show_other_alloys):
        # compute top families based on currently filtered data
        fam_series_plot = df_filtered_scatter["FamilyKey"].replace("", np.nan).dropna()
        fam_counts_plot = fam_series_plot.value_counts()
        families_all_plot = fam_counts_plot.index.tolist()
        try:
            max_family_controls_val = int(st.session_state.get("scatter_max_families", 10))
            if max_family_controls_val < 1:
                max_family_controls_val = 1
        except Exception:
            max_family_controls_val = 10
        sel_from_session = st.session_state.get("family_style_selector", None)
        if isinstance(sel_from_session, list) and len(sel_from_session) > 0:
            sel_trimmed = sel_from_session[:max_family_controls_val]
            top_fams_plot = sel_trimmed
        else:
            top_fams_plot = families_all_plot[:max_family_controls_val]
        if len(top_fams_plot) > 0:
            df_for_autoscale = df_filtered_scatter[df_filtered_scatter["FamilyKey"].isin(top_fams_plot)]
            if not df_for_autoscale.empty:
                a_xmin, a_xmax = autoscale_axis_asymmetric(df_for_autoscale[x_col], left_factor=1.1, right_factor=1.6)
                a_ymin, a_ymax = autoscale_axis(df_for_autoscale[y_col], expand_factor=1.1)

    # Initialize axis limits in session if not present
    if "axis_limits" not in st.session_state:
        st.session_state["axis_limits"] = {"xmin": a_xmin, "xmax": a_xmax, "ymin": a_ymin, "ymax": a_ymax}

    # Update session axis limits unless locked
    if not lock_axes:
        st.session_state["axis_limits"]["xmin"] = a_xmin
        st.session_state["axis_limits"]["xmax"] = a_xmax
        st.session_state["axis_limits"]["ymin"] = a_ymin
        st.session_state["axis_limits"]["ymax"] = a_ymax

    # Axis limits inputs (4 number_inputs)
    st.markdown("**Axis limits**")
    ax1, ax2, ax3, ax4 = st.columns(4)
    with ax1:
        xmin_key = f"num_xmin_{a_xmin:.4f}" if not lock_axes else "num_xmin_locked"
        xmin = st.number_input("Xmin", value=float(st.session_state["axis_limits"]["xmin"]), format="%.4f", key=xmin_key)
        st.session_state["axis_limits"]["xmin"] = float(xmin)
    with ax2:
        xmax_key = f"num_xmax_{a_xmax:.4f}" if not lock_axes else "num_xmax_locked"
        xmax = st.number_input("Xmax", value=float(st.session_state["axis_limits"]["xmax"]), format="%.4f", key=xmax_key)
        st.session_state["axis_limits"]["xmax"] = float(xmax)
    with ax3:
        ymin_key = f"num_ymin_{a_ymin:.4f}" if not lock_axes else "num_ymin_locked"
        ymin = st.number_input("Ymin", value=float(st.session_state["axis_limits"]["ymin"]), format="%.4f", key=ymin_key)
        st.session_state["axis_limits"]["ymin"] = float(ymin)
    with ax4:
        ymax_key = f"num_ymax_{a_ymax:.4f}" if not lock_axes else "num_ymax_locked"
        ymax = st.number_input("Ymax", value=float(st.session_state["axis_limits"]["ymax"]), format="%.4f", key=ymax_key)
        st.session_state["axis_limits"]["ymax"] = float(ymax)

    if add_marker_border:
        r4c1, r4c2, r4c3, r4c4, r4c5, r4c6 = st.columns([1,1,1,1,1,1], gap="small")
        with r4c1:
            bg = st.color_picker("Background", "#262e40", key="scatter_bg")
        with r4c2:
            axis_color = st.color_picker("Axis color", "#ffffff", key="scatter_axis_color")
        with r4c3:
            marker_border_color = st.color_picker("Marker border color", "#ffffff", key="scatter_marker_border_color")
        with r4c4:
            marker_size = st.slider("Marker size", 4, 24, 9, key="scatter_markersize")
        with r4c5:
            marker_opacity = st.slider("Marker opacity", 0.1, 1.0, 0.9, step=0.05, key="scatter_markerop")
        with r4c6:
            marker_border_width = st.slider("Marker border width", 0.0, 4.0, 0.8, step=0.1, key="scatter_marker_border_width")
    else:
        r4c1, r4c2, r4c3, r4c4 = st.columns([1,1,1,1], gap="small")
        with r4c1:
            bg = st.color_picker("Background", "#262e40", key="scatter_bg")
        with r4c2:
            axis_color = st.color_picker("Axis color", "#ffffff", key="scatter_axis_color")
        with r4c3:
            marker_size = st.slider("Marker size", 4, 24, 9, key="scatter_markersize")
        with r4c4:
            marker_opacity = st.slider("Marker opacity", 0.1, 1.0, 0.9, step=0.05, key="scatter_markerop")
        marker_border_color = st.session_state.get("scatter_marker_border_color", "#ffffff")
        marker_border_width = 0.0

    if plot_alloy_names:
        alloy_name_size = st.slider("Alloy Name Size", 6, 36, 12, key="alloy_name_size")
    else:
        alloy_name_size = st.session_state.get("alloy_name_size", 12)

    # Styling mode radio (By User, By Complexity, By Family)
    style_mode = st.radio("Styling mode", ["By User", "By Complexity", "By Family"], index=0, key="scatter_styling_mode")

    # If family mode — show max families control plus placeholder for family multiselect
    if style_mode == "By Family":
        st.write("")
        left_col, right_col = st.columns([3,7], gap="small")
        with left_col:
            max_family_controls = st.number_input("Max families to show (family mode)", 1, 400, 10, key="scatter_max_families")
        with right_col:
            family_select_placeholder = st.empty()
    else:
        max_family_controls = None
        family_select_placeholder = None

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------
# Use updated axis_limits values
# ---------------------------
xmin = float(st.session_state["axis_limits"]["xmin"])
xmax = float(st.session_state["axis_limits"]["xmax"])
ymin = float(st.session_state["axis_limits"]["ymin"])
ymax = float(st.session_state["axis_limits"]["ymax"])

with st.expander("Extra editing options"):
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    extra_edit_cols = st.columns([15, 15, 15, 15, 10, 10, 10, 10], gap="small")

    with extra_edit_cols[0]:
        selected_line_style_label = st.selectbox(
            "Line Plot",
            options=list(LINE_STYLE_OPTIONS.keys()),
            index=0,
            key="scatter_group_line_style_label",
        )

    with extra_edit_cols[1]:
        line_width = st.slider("Line width", 1, 12, 2, key="scatter_group_line_width")

    with extra_edit_cols[2]:
        line_opacity = st.slider("Line opacity", 0.1, 1.0, 0.9, step=0.05, key="scatter_group_line_opacity")

    with extra_edit_cols[3]:
        download_button_placeholder = st.empty()

    with extra_edit_cols[4]:
        download_width = st.number_input(
            "Width (px)",
            min_value=400,
            max_value=5000,
            value=DOWNLOAD_BASE_WIDTH,
            step=100,
            key="scatter_download_width",
            on_change=sync_download_from_width,
        )

    with extra_edit_cols[5]:
        download_height = st.number_input(
            "Height (px)",
            min_value=300,
            max_value=5000,
            value=DOWNLOAD_BASE_HEIGHT,
            step=100,
            key="scatter_download_height",
            on_change=sync_download_from_height,
        )

    with extra_edit_cols[6]:
        download_scale = st.number_input(
            "Scale",
            min_value=0.5,
            max_value=5.0,
            value=1.0,
            step=0.1,
            format="%.1f",
            key="scatter_download_scale",
            on_change=sync_download_from_scale,
        )

    with extra_edit_cols[7]:
        download_format = st.selectbox(
            "Download format",
            options=["png", "svg", "jpeg", "webp"],
            index=0,
            key="scatter_download_format",
        )

    with download_button_placeholder:
        st_html(
            f"""
            <style>
            #scatter-download-button {{
              width: 100%;
              min-height: 38px;
              background: linear-gradient(145deg, #232735, #4c3a3a);
              color: #ffffff;
              border-radius: 10px;
              border: 1px solid #4c4d52;
              padding: 8px 18px;
              font-weight: 600;
              font-size: 0.95rem;
              cursor: pointer;
              transition: all 0.3s ease;
            }}
            #scatter-download-button:hover {{
              transform: translateY(-2px);
              box-shadow: 4px 4px 8px #0f111a, -4px -4px 8px #252933;
            }}
            #scatter-download-button:active {{
              transform: scale(0.97);
              box-shadow: inset 2px 2px 5px #0f111a, inset -2px -2px 5px #252933;
            }}
            </style>
            <div style="padding-top: 28px;">
              <button id="scatter-download-button">
                Download plot
              </button>
            </div>
            <script>
            const button = document.getElementById("scatter-download-button");
            if (button) {{
              button.onclick = function () {{
                const parentDoc = window.parent.document;
                const plots = parentDoc.querySelectorAll('div[data-testid="stPlotlyChart"] .js-plotly-plot');
                const scatterPlot = plots && plots.length ? plots[0] : null;
                if (!scatterPlot) {{
                  window.alert("Scatter plot not found for download.");
                  return;
                }}

                const parentPlotly = window.parent.Plotly;
                if (parentPlotly && typeof parentPlotly.downloadImage === "function") {{
                  parentPlotly.downloadImage(scatterPlot, {{
                    format: "{download_format}",
                    filename: "interactive_scatter",
                    width: {int(download_width)},
                    height: {int(download_height)},
                    scale: {float(download_scale)},
                  }});
                  return;
                }}

                const modebarButtons = parentDoc.querySelectorAll('div[data-testid="stPlotlyChart"] .modebar-btn');
                for (const item of modebarButtons) {{
                  const label = (item.getAttribute("data-title") || item.getAttribute("aria-label") || item.getAttribute("title") || "").toLowerCase();
                  if (label.includes("download plot")) {{
                    item.click();
                    return;
                  }}
                }}

                window.alert("Plot download is not available in this browser view.");
              }};
            }}
            </script>
            """,
            height=76,
        )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    heatmap_cols = st.columns([14, 12, 8, 8, 8, 10, 10, 10, 10, 10], gap="small")

    heatmap_axis_options = ["None"] + all_plot_columns
    with heatmap_cols[0]:
        heatmap_z_col = st.selectbox(
            "Heat map axis",
            options=heatmap_axis_options,
            index=0,
            key="scatter_heatmap_axis",
        )
    with heatmap_cols[1]:
        heatmap_scale_label = st.selectbox(
            "Heat map scale",
            options=list(HEATMAP_SCALE_OPTIONS.keys()),
            index=0,
            key="scatter_heatmap_scale",
        )
    with heatmap_cols[2]:
        reverse_heatmap_scale = st.checkbox("Reverse", value=False, key="scatter_heatmap_reverse")
    with heatmap_cols[3]:
        show_heatmap_bar = st.checkbox("Color bar", value=True, key="scatter_heatmap_show_bar")
    with heatmap_cols[4]:
        heatmap_autorange = st.checkbox("Auto range", value=True, key="scatter_heatmap_autorange")
    with heatmap_cols[5]:
        heatmap_zmin = st.number_input("Z min", value=0.0, format="%.4f", key="scatter_heatmap_zmin")
    with heatmap_cols[6]:
        heatmap_zmax = st.number_input("Z max", value=1.0, format="%.4f", key="scatter_heatmap_zmax")
    with heatmap_cols[7]:
        heatmap_bar_width = st.slider("Bar width", 8, 40, 16, key="scatter_heatmap_bar_width")
    with heatmap_cols[8]:
        heatmap_bar_length = st.slider("Bar height", 0.2, 1.0, 0.75, step=0.05, key="scatter_heatmap_bar_length")
    with heatmap_cols[9]:
        heatmap_bar_position = st.selectbox(
            "Bar position",
            options=["Right", "Left", "Above", "Below"],
            index=0,
            key="scatter_heatmap_bar_position",
        )

    heatmap_enabled_local = heatmap_z_col != "None"
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    title_cols = st.columns([18, 18, 10, 18], gap="small")
    with title_cols[0]:
        x_axis_title_override = st.text_input(
            "X axis title",
            value="",
            key="scatter_x_axis_title_override",
            placeholder="Leave blank to use selected X axis",
        )
    with title_cols[1]:
        y_axis_title_override = st.text_input(
            "Y axis title",
            value="",
            key="scatter_y_axis_title_override",
            placeholder="Leave blank to use selected Y axis",
        )
    with title_cols[2]:
        show_legend = st.checkbox("Show legend", value=True, key="scatter_show_legend")
    with title_cols[3]:
        if heatmap_enabled_local:
            heatmap_heading_override = st.text_input(
                "Heat map heading",
                value="",
                key="scatter_heatmap_heading_override",
                placeholder="Leave blank to use heat map axis name",
            )
        else:
            heatmap_heading_override = ""

selected_group_line_style = LINE_STYLE_OPTIONS[selected_line_style_label]
selected_heatmap_scale = HEATMAP_SCALE_OPTIONS[heatmap_scale_label]
heatmap_enabled = heatmap_z_col != "None"
x_axis_title_final = x_axis_title_override.strip() or x_col
y_axis_title_final = y_axis_title_override.strip() or y_col
heatmap_heading_final = heatmap_heading_override.strip() or heatmap_z_col


# ---------------------------
# Session maps & pagination
# ---------------------------
if "color_map_user" not in st.session_state:
    st.session_state["color_map_user"] = {}
if "symbol_map_user" not in st.session_state:
    st.session_state["symbol_map_user"] = {}
if "color_map_complex" not in st.session_state:
    st.session_state["color_map_complex"] = {}
if "symbol_map_complex" not in st.session_state:
    st.session_state["symbol_map_complex"] = {}
if "color_map_family" not in st.session_state:
    st.session_state["color_map_family"] = {}
if "symbol_map_family" not in st.session_state:
    st.session_state["symbol_map_family"] = {}

if "user_page_index" not in st.session_state:
    st.session_state["user_page_index"] = 0
if "family_page_index" not in st.session_state:
    st.session_state["family_page_index"] = 0

DEFAULT_PAGE_SIZE = 6
FAMILY_PAGE_SIZE = 4


# ---------------------------
# Styling Controls (Pagination)
# ---------------------------
with col_controls:
    st.markdown("**Styling Controls**")

    if style_mode == "By User":
        users_present = sorted(df_filtered_scatter["user"].dropna().unique())
        if not users_present:
            st.info("No users in filtered data.")
        else:
            total = len(users_present)
            page = st.session_state["user_page_index"]
            page_size = DEFAULT_PAGE_SIZE
            start = page * page_size
            end = min(start + page_size, total)

            st.markdown('<div class="users-pager">', unsafe_allow_html=True)
            pcol1, _, pcol3 = st.columns([3,8,3])
            with pcol1:
                if st.button("Prev users", key="prev_users"):
                    st.session_state["user_page_index"] = max(0, st.session_state["user_page_index"] - 1)
            with pcol3:
                if st.button("Next users", key="next_users"):
                    if end < total:
                        st.session_state["user_page_index"] += 1
            st.markdown('</div>', unsafe_allow_html=True)

            visible = users_present[start:end]
            cols = st.columns(len(visible))
            for col_widget, u in zip(cols, visible):
                with col_widget:
                    st.markdown(f"<div class='user-card'><div class='user-card-title'>{u}</div></div>", unsafe_allow_html=True)
                    c_col, s_col = st.columns([1,3], gap="small")
                    with c_col:
                        default_c = st.session_state["color_map_user"].get(u, DEFAULT_COLORS[users_present.index(u) % len(DEFAULT_COLORS)])
                        c = st.color_picker("", value=default_c, key=f"color_user_{u}")
                        st.session_state["color_map_user"][u] = c
                    with s_col:
                        default_s = st.session_state["symbol_map_user"].get(u, MARKER_OPTIONS[users_present.index(u) % len(MARKER_OPTIONS)])
                        s = st.selectbox("", MARKER_OPTIONS, index=MARKER_OPTIONS.index(default_s) if default_s in MARKER_OPTIONS else 0, key=f"symbol_user_{u}")
                        st.session_state["symbol_map_user"][u] = s

    elif style_mode == "By Complexity":
        complex_present = sorted(df_filtered_scatter["complexity"].dropna().unique())
        if not complex_present:
            st.info("No complexities present.")
        else:
            cols = st.columns(len(complex_present))
            for col_widget, cplx in zip(cols, complex_present):
                with col_widget:
                    st.markdown(f"<div class='user-card'><div class='user-card-title'>{cplx}</div></div>", unsafe_allow_html=True)
                    c_col, s_col = st.columns([1,3], gap="small")
                    with c_col:
                        default_c = st.session_state["color_map_complex"].get(cplx, DEFAULT_COLORS[complex_present.index(cplx) % len(DEFAULT_COLORS)])
                        c = st.color_picker("", value=default_c, key=f"color_complex_{cplx}")
                        st.session_state["color_map_complex"][cplx] = c
                    with s_col:
                        default_s = st.session_state["symbol_map_complex"].get(cplx, MARKER_OPTIONS[complex_present.index(cplx) % len(MARKER_OPTIONS)])
                        s = st.selectbox("", MARKER_OPTIONS, index=MARKER_OPTIONS.index(default_s) if default_s in MARKER_OPTIONS else 0, key=f"symbol_complex_{cplx}")
                        st.session_state["symbol_map_complex"][cplx] = s

    elif style_mode == "By Family":
        fam_series = df_filtered_scatter["FamilyKey"].replace("", np.nan).dropna()
        fam_counts = fam_series.value_counts()
        if fam_counts.empty:
            st.info("No families found.")
        else:
            families_all = fam_counts.index.tolist()
            max_family_controls_val = int(max_family_controls) if max_family_controls is not None else 10
            if max_family_controls_val < 1:
                max_family_controls_val = 1

            default_selected = families_all[:max_family_controls_val]
            chosen = family_select_placeholder.multiselect(
                f"Pick up to {max_family_controls_val} families to style (out of {len(families_all)})",
                options=families_all,
                default=default_selected,
                key="family_style_selector"
            )

            if isinstance(chosen, list) and len(chosen) > max_family_controls_val:
                chosen = chosen[:max_family_controls_val]
                st.session_state["family_style_selector"] = chosen
                st.warning(f"Selection trimmed to the first {max_family_controls_val} families because that's the current max.")

            if isinstance(chosen, list) and len(chosen) > 0:
                families_for_plot = chosen
            else:
                families_for_plot = default_selected

            total = len(families_for_plot)
            page = st.session_state["family_page_index"]
            page_size = FAMILY_PAGE_SIZE
            start = page * page_size
            end = min(start + page_size, total)

            st.markdown('<div class="families-pager">', unsafe_allow_html=True)
            pcol1, _, pcol3 = st.columns([3,8,3])
            with pcol1:
                if st.button("Prev families", key="prev_families"):
                    st.session_state["family_page_index"] = max(0, st.session_state["family_page_index"] - 1)
            with pcol3:
                if st.button("Next families", key="next_families"):
                    if end < total:
                        st.session_state["family_page_index"] += 1
            st.markdown('</div>', unsafe_allow_html=True)

            visible = families_for_plot[start:end]
            if visible:
                cols = st.columns(len(visible))
                for col_widget, fam in zip(cols, visible):
                    with col_widget:
                        st.markdown(f"<div class='family-card family-control'><div class='family-card-title'>{fam} (n={fam_counts[fam]})</div></div>", unsafe_allow_html=True)
                        default_c = st.session_state["color_map_family"].get(fam, DEFAULT_COLORS[families_all.index(fam) % len(DEFAULT_COLORS)])
                        c_col, s_col = st.columns([1,3], gap="small")
                        with c_col:
                            c = st.color_picker("", value=default_c, key=f"color_family_{fam}")
                            st.session_state["color_map_family"][fam] = c
                        with s_col:
                            default_s = st.session_state["symbol_map_family"].get(fam, MARKER_OPTIONS[families_all.index(fam) % len(MARKER_OPTIONS)])
                            s = st.selectbox("", MARKER_OPTIONS, index=MARKER_OPTIONS.index(default_s) if default_s in MARKER_OPTIONS else 0, key=f"symbol_family_{fam}")
                            st.session_state["symbol_map_family"][fam] = s

            if total > page_size:
                st.caption(f"Showing {start+1}-{end} of {total} selected families. Use Prev/Next to page.")
            else:
                st.caption(f"Showing {start+1}-{end} of {total} selected families.")


# ---------------------------
# Helper utilities for hover and alloy formatting
# ---------------------------
_sub_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
def to_subscript(num):
    try:
        i = int(round(num))
    except Exception:
        i = int(num)
    return str(i).translate(_sub_digits)

_formula_re = re.compile(r"([A-Z][a-z]?)(\d*)")
def parse_alloy_formula(formula):
    parts = _formula_re.findall(str(formula))
    d = {}
    total = 0
    for el, cnt in parts:
        if cnt == "":
            cnt_i = 1
        else:
            try:
                cnt_i = int(cnt)
            except Exception:
                cnt_i = int(float(cnt))
        d[el] = cnt_i
        total += cnt_i
    return d, total


# ---------------------------
# PLOTTING BLOCK (robust alloy-name + autoscale fix)
# ---------------------------
with scatter_placeholder:
    plotting_df = df_filtered_scatter.copy()

    def make_hover_fields(row):
        alloy_raw = row.get("alloy", "")
        parsed, total = parse_alloy_formula(alloy_raw)
        alloy_percent_parts = []
        if total > 0:
            for el, cnt in parsed.items():
                pct = round((cnt / total) * 100)
                alloy_percent_parts.append(f"{el}{to_subscript(pct)}")
        alloy_title = "".join(alloy_percent_parts) if alloy_percent_parts else str(alloy_raw)

        def fmt(v):
            try:
                return f"{float(v):.4g}"
            except Exception:
                return str(v)

        x_val = fmt(row.get(x_col, ""))
        y_val = fmt(row.get(y_col, ""))
        user_val = row.get("user", "")
        family_val = row.get("FamilyKey", "")

        return pd.Series({
            "_hover_title": alloy_title,
            "_xval": f"{x_col} = {x_val}",
            "_yval": f"{y_col} = {y_val}",
            "_user": f"{user_val}",
            "_alloy_raw": f"{alloy_raw}",
            "_family": f"{family_val}",
        })

    hover_df = plotting_df.apply(make_hover_fields, axis=1)
    for c in hover_df.columns:
        plotting_df[c] = hover_df[c]

    heatmap_zmin_final = None
    heatmap_zmax_final = None
    if heatmap_enabled:
        plotting_df[heatmap_z_col] = pd.to_numeric(plotting_df[heatmap_z_col], errors="coerce")
        plotting_df = plotting_df.dropna(subset=[heatmap_z_col])
        if plotting_df.empty:
            st.warning("No rows remain after applying the selected heat map axis.")
        else:
            z_series = plotting_df[heatmap_z_col]
            zmin_auto = float(z_series.min())
            zmax_auto = float(z_series.max())
            if heatmap_autorange:
                heatmap_zmin_final = zmin_auto
                heatmap_zmax_final = zmax_auto
            else:
                heatmap_zmin_final = float(heatmap_zmin)
                heatmap_zmax_final = float(heatmap_zmax)

    # Ensure alloy_name_size in session (safe fallback)
    alloy_name_size = st.session_state.get("alloy_name_size", 12)

    # Handle By Family __others__ hiding for plotting (and earlier autoscale fix ensures axis used visible rows)
    if style_mode == "By Family":
        fam_series_plot = plotting_df["FamilyKey"].replace("", np.nan).dropna()
        fam_counts_plot = fam_series_plot.value_counts()
        families_all_plot = fam_counts_plot.index.tolist()
        max_family_controls_val = int(max_family_controls) if max_family_controls is not None else 10
        if max_family_controls_val < 1:
            max_family_controls_val = 1
        sel_from_session = st.session_state.get("family_style_selector", None)
        if isinstance(sel_from_session, list) and len(sel_from_session) > 0:
            sel_trimmed = sel_from_session[:max_family_controls_val]
            top_fams_plot = sel_trimmed
        else:
            top_fams_plot = families_all_plot[:max_family_controls_val]

        plotting_df["FamilyForColor"] = plotting_df["FamilyKey"].where(plotting_df["FamilyKey"].isin(top_fams_plot), "__others__")

        if not show_other_alloys:
            plotting_df = plotting_df[plotting_df["FamilyForColor"] != "__others__"]

    color_arg = None
    symbol_arg = None
    color_map = {}
    symbol_map = {}
    group_order_col = None

    if style_mode == "By User":
        color_arg = "user"
        symbol_arg = "user"
        group_order_col = "user"
        users_present = sorted(plotting_df["user"].dropna().unique())
        for i, u in enumerate(users_present):
            color_map[u] = st.session_state["color_map_user"].get(u, DEFAULT_COLORS[i % len(DEFAULT_COLORS)])
            symbol_map[u] = st.session_state["symbol_map_user"].get(u, MARKER_OPTIONS[i % len(MARKER_OPTIONS)])
    elif style_mode == "By Complexity":
        color_arg = "complexity"
        symbol_arg = "complexity"
        group_order_col = "complexity"
        comps_present = sorted(plotting_df["complexity"].dropna().unique())
        for i, cplx in enumerate(comps_present):
            color_map[cplx] = st.session_state["color_map_complex"].get(cplx, DEFAULT_COLORS[i % len(DEFAULT_COLORS)])
            symbol_map[cplx] = st.session_state["symbol_map_complex"].get(cplx, MARKER_OPTIONS[i % len(MARKER_OPTIONS)])
    elif style_mode == "By Family":
        color_arg = "FamilyForColor"
        symbol_arg = "FamilyForColor"
        group_order_col = "FamilyForColor"
        fam_series_plot = plotting_df["FamilyKey"].replace("", np.nan).dropna()
        fam_counts_plot = fam_series_plot.value_counts()
        families_all_plot = fam_counts_plot.index.tolist()
        max_family_controls_val = int(max_family_controls) if max_family_controls is not None else 10
        if max_family_controls_val < 1:
            max_family_controls_val = 1
        sel_from_session = st.session_state.get("family_style_selector", None)
        if isinstance(sel_from_session, list) and len(sel_from_session) > 0:
            sel_trimmed = sel_from_session[:max_family_controls_val]
            top_fams_plot = sel_trimmed
        else:
            top_fams_plot = families_all_plot[:max_family_controls_val]

        for i, fam in enumerate(top_fams_plot):
            color_map[fam] = st.session_state["color_map_family"].get(fam, DEFAULT_COLORS[i % len(DEFAULT_COLORS)])
            symbol_map[fam] = st.session_state["symbol_map_family"].get(fam, MARKER_OPTIONS[i % len(MARKER_OPTIONS)])

        color_map["__others__"] = st.session_state["color_map_family"].get("__others__", "#888888")
        symbol_map["__others__"] = st.session_state["symbol_map_family"].get("__others__", MARKER_OPTIONS[len(top_fams_plot) % len(MARKER_OPTIONS)])

    try:
        custom_cols = ["_hover_title", "_xval", "_yval", "_user", "_alloy_raw", "_family"]

        if selected_group_line_style and group_order_col and group_order_col in plotting_df.columns:
            plotting_df = plotting_df.sort_values(by=[group_order_col, x_col], kind="stable")

        # Ensure text column exists for safe use when plot_alloy_names True
        if "_hover_title" not in plotting_df.columns:
            plotting_df["_hover_title"] = plotting_df.get("alloy", "").astype(str)

        scatter_kwargs = dict(
            data_frame=plotting_df,
            x=x_col,
            y=y_col,
            symbol=symbol_arg,
            custom_data=custom_cols,
            labels={x_col: x_col, y_col: y_col},
        )
        if heatmap_enabled:
            heatmap_scale_values = list(selected_heatmap_scale)
            if reverse_heatmap_scale:
                heatmap_scale_values = list(reversed(heatmap_scale_values))
            scatter_kwargs["color"] = heatmap_z_col
            scatter_kwargs["color_continuous_scale"] = heatmap_scale_values
            if heatmap_zmin_final is not None and heatmap_zmax_final is not None:
                scatter_kwargs["range_color"] = [heatmap_zmin_final, heatmap_zmax_final]
            scatter_kwargs["labels"][heatmap_z_col] = heatmap_z_col
        else:
            scatter_kwargs["color"] = color_arg

        if plot_alloy_names:
            fig = px.scatter(
                text="_hover_title",
                **scatter_kwargs,
            )
        else:
            fig = px.scatter(
                **scatter_kwargs,
            )

        hovertemplate = (
            "<b>%{customdata[0]}</b><br>"
            "%{customdata[1]}<br>"
            "%{customdata[2]}<br>"
            "User = %{customdata[3]}<br>"
            "Alloy (raw) = %{customdata[4]}<br>"
            "Family = %{customdata[5]}<extra></extra>"
        )

        for trace in fig.data:
            # marker size & opacity
            try:
                trace.marker.size = marker_size
                trace.marker.opacity = marker_opacity
                trace.marker.line = dict(color=marker_border_color, width=marker_border_width)
            except Exception:
                pass

            # color & symbol mapping
            name = getattr(trace, "name", None)
            if (not heatmap_enabled) and name is not None:
                if name in color_map:
                    try:
                        trace.marker.color = color_map[name]
                    except Exception:
                        pass
                if name in symbol_map:
                    try:
                        trace.marker.symbol = symbol_map[name]
                    except Exception:
                        pass

            if selected_group_line_style:
                try:
                    trace.mode = "lines+markers"
                    trace.line.dash = selected_group_line_style
                    trace.line.width = line_width
                    if (not heatmap_enabled) and name in color_map:
                        trace.line.color = color_with_alpha(color_map[name], line_opacity)
                    else:
                        trace.line.color = color_with_alpha(marker_border_color, line_opacity)
                except Exception:
                    pass
            else:
                try:
                    trace.mode = "markers+text" if plot_alloy_names else "markers"
                except Exception:
                    pass

            # hovertemplate
            try:
                trace.hovertemplate = hovertemplate
            except Exception:
                pass

            # alloy name text styling if enabled
            if plot_alloy_names:
                try:
                    if hasattr(trace, "textfont"):
                        trace.textfont = dict(size=int(alloy_name_size), color=axis_color)
                    else:
                        trace.update(textfont=dict(size=int(alloy_name_size), color=axis_color))
                    trace.textposition = "top center"
                except Exception:
                    pass

        fig.update_layout(
            hoverlabel=dict(
                bgcolor="rgba(18,18,18,0.95)",
                bordercolor="rgba(255,255,255,0.12)",
                font=dict(color="#ffffff", size=12, family="Arial")
            )
        )
        if heatmap_enabled:
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title=dict(text=heatmap_heading_final, font=dict(color=axis_color)),
                    tickfont=dict(color=axis_color),
                    outlinewidth=0,
                    bgcolor="rgba(0,0,0,0)",
                    thickness=heatmap_bar_width,
                    len=heatmap_bar_length,
                )
            )
            if heatmap_bar_position == "Left":
                fig.update_layout(
                    coloraxis_colorbar=dict(
                        x=-0.12,
                        xanchor="right",
                        y=0.5,
                        yanchor="middle",
                    )
                )
            elif heatmap_bar_position == "Above":
                fig.update_layout(
                    coloraxis_colorbar=dict(
                        orientation="h",
                        x=0.5,
                        xanchor="center",
                        y=1.12,
                        yanchor="bottom",
                    )
                )
            elif heatmap_bar_position == "Below":
                fig.update_layout(
                    coloraxis_colorbar=dict(
                        orientation="h",
                        x=0.5,
                        xanchor="center",
                        y=-0.28,
                        yanchor="top",
                    )
                )
            else:
                fig.update_layout(
                    coloraxis_colorbar=dict(
                        x=1.02,
                        xanchor="left",
                        y=0.5,
                        yanchor="middle",
                    )
                )
            if not show_heatmap_bar:
                fig.update_layout(coloraxis_showscale=False)
            else:
                fig.update_layout(coloraxis_showscale=True)

    except Exception as e:
        st.error(f"Error building scatter: {e}")
        fig = go.Figure()

    # Apply axis ranges and axis title/tick styling
    fig.update_xaxes(range=[xmin, xmax], title_text=x_axis_title_final, showgrid=False, showline=True, linecolor=axis_color, tickfont=dict(size=14, color=axis_color), title_font=dict(size=16, color=axis_color))
    fig.update_yaxes(range=[ymin, ymax], title_text=y_axis_title_final, showgrid=False, showline=True, linecolor=axis_color, tickfont=dict(size=14, color=axis_color), title_font=dict(size=16, color=axis_color))

    # compute height from mode
    fig_height = get_plot_height_for_mode(style_mode)

    fig.update_layout(
        plot_bgcolor=bg,
        paper_bgcolor=bg,
        height=fig_height,
        legend=dict(
            x=0.92,
            y=0.98,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(color=axis_color)
        ),
        legend_title_font=dict(color=axis_color),
        showlegend=show_legend,
        margin=dict(l=40, r=20, t=30, b=40)
    )

    # Render
    scatter_plot_config = {
        "displaylogo": False,
        "toImageButtonOptions": {
            "format": download_format,
            "filename": "interactive_scatter",
            "width": int(download_width),
            "height": int(download_height),
            "scale": float(download_scale),
        },
    }
    st.plotly_chart(fig, width="stretch", config=scatter_plot_config)



















# ---------------------------
# INTERACTIVE DOS - Multple DOS combination implemented
# ---------------------------

# pro_interactive_dos.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os
import re
import hashlib
import colorsys
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d

st.set_page_config(layout="wide")
st.subheader("📊 Pro Interactive DOS")

# ---------------------------
# Helpers & parsing
# ---------------------------
_sub_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

def to_subscript(num):
    try:
        i = int(round(num))
    except Exception:
        i = int(float(num))
    return str(i).translate(_sub_digits)

_formula_re = re.compile(r"([A-Z][a-z]?)(\d*)")

def parse_alloy_formula(formula):
    parts = _formula_re.findall(str(formula))
    d = {}
    total = 0
    for el, cnt in parts:
        if cnt == "":
            cnt_i = 1
        else:
            try:
                cnt_i = int(cnt)
            except Exception:
                cnt_i = int(float(cnt))
        d[el] = cnt_i
        total += cnt_i
    return d, total

def alloy_unicode_title(alloy_raw):
    parsed, total = parse_alloy_formula(alloy_raw)
    parts = []
    if total > 0:
        for el, cnt in parsed.items():
            pct = round((cnt / total) * 100)
            parts.append(f"{el}{to_subscript(pct)}")
        return "".join(parts)
    return str(alloy_raw)

def safe_key(s: str) -> str:
    return re.sub(r"[^0-9a-zA-Z_]", "_", str(s))

# Deterministic vibrant color generator (spread across hues, visible on dark bg)
def vibrant_color_from_key(key: str):
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16)
    hue = ((h % 360) / 360.0)
    golden = 0.61803398875
    hue = (hue + ((h >> 8) * golden) % 1.0) % 1.0
    sat = 0.5 + ((h >> 16) % 40) / 100.0   # 0.5 - 0.9
    val = 0.7 + ((h >> 24) % 30) / 100.0   # 0.7 - 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, min(sat, 0.95), min(val, 0.98))
    return "#{0:02x}{1:02x}{2:02x}".format(int(r * 255), int(g * 255), int(b * 255))

def two_distinct_colors(key_base: str):
    c1 = vibrant_color_from_key(key_base + "_A")
    c2 = vibrant_color_from_key(key_base + "_B")
    if c1 == c2:
        c2 = vibrant_color_from_key(key_base + "_C")
    return c1, c2

# Gaussian smearing helper
def smooth_dos(energy, dos, sigma_ev):
    if sigma_ev is None or sigma_ev <= 0:
        return dos
    energy = np.asarray(energy)
    dos = np.asarray(dos)
    if len(energy) < 2:
        return dos

    dE = np.mean(np.diff(energy))
    if not np.isfinite(dE) or dE == 0:
        return dos

    sigma_pts = max(1, int(round(float(sigma_ev) / abs(dE))))
    return gaussian_filter1d(dos, sigma_pts)

# ---------------------------
# File loaders
# ---------------------------
@st.cache_data
def load_tdos(path):
    data = np.loadtxt(path)
    return data[:, 0], data[:, 1]

@st.cache_data
def load_pdos(path):
    with open(path) as f:
        lines = f.readlines()
    header_line = None
    for line in lines:
        if line.strip().startswith("#"):
            header_line = line.strip()
            break
    if header_line is None:
        raise ValueError("PDOS header not found")
    cols = header_line.replace("#", "").split()
    n_cols = len(cols)
    values = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        for p in parts:
            try:
                values.append(float(p))
            except ValueError:
                pass
    values = np.array(values)
    n_rows = len(values) // n_cols
    data = values[: n_rows * n_cols].reshape(n_rows, n_cols)
    df = pd.DataFrame(data, columns=cols)
    return df

# ---------------------------
# Small plot container tweak
# ---------------------------
st.markdown(
    """
<style>
div[data-testid="stPlotlyChart"] > div { border-radius: 12px; overflow: hidden; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# Input DF
# ---------------------------
try:
    _ = filtered_df
except NameError:
    st.error("`filtered_df` not found. Please load your DataFrame as `filtered_df` and re-run.")
    st.stop()

df_master = filtered_df.copy()

# Create FamilyKey if missing
if "FamilyKey" not in df_master.columns:
    try:
        elements_cols = [c for c in df_master.columns if c.endswith("_present")]

        def make_family_key_from_row(row):
            present = []
            for c in elements_cols:
                try:
                    vv = int(float(row[c]))
                except Exception:
                    vv = 1 if pd.notna(row[c]) and str(row[c]).strip() not in ["0", "0.0", "False", "false", ""] else 0
                if vv:
                    present.append(c.replace("_present", ""))
            return "-".join(sorted(present)) if present else ""

        df_master["FamilyKey"] = df_master.apply(make_family_key_from_row, axis=1)
    except Exception:
        df_master["FamilyKey"] = df_master.get("alloy", "").astype(str)

# ---------------------------
# Plot height helper
# ---------------------------
def get_plot_height_for_mode(style_mode: str, n_selected: int) -> int:
    if style_mode == "Individual":
        return 580 if n_selected == 0 else 810
    if style_mode == "Family":
        return 670 if n_selected == 0 else 900
    return 800

# ---------------------------
# UI layout: columns
# ---------------------------
col_plot, col_controls = st.columns([1.2, 1])

# ---------------------------
# Controls
# ---------------------------
with col_controls:
    st.markdown('<div class="controls-section">', unsafe_allow_html=True)

    # Split the row into two columns:
    # left = styling mode, right = gaussian smearing
    mode_col, smear_col = st.columns([1, 1], gap="small")
    with mode_col:
        style_mode = st.radio("Styling mode", ["Individual", "Family"], index=0, key="dos_styling_mode")
    with smear_col:
        sigma_ev = st.number_input(
            "Gaussian smearing (eV)",
            min_value=0.0,
            max_value=1.0,
            value=0.06,
            step=0.01,
            format="%.2f",
            key="dos_sigma_ev",
        )

    # Row: users + alloys/families
    st.write("")
    r1c1, r1c2 = st.columns([1, 1])
    with r1c1:
        users = sorted(df_master["user"].dropna().unique().tolist())
        selected_users = st.multiselect("Choose users", options=users, default=users, key="dos_users")

    # prepare alloy display mapping
    unique_rows = df_master[["alloy", "atom_count"]].drop_duplicates()
    alloy_display_map = {}
    for _, rw in unique_rows.iterrows():
        orig = rw["alloy"]
        total = rw.get("atom_count", None) or 0
        try:
            total = int(total)
        except Exception:
            try:
                total = int(float(total))
            except Exception:
                total = 0
        display = alloy_unicode_title(orig) if total else str(orig)
        if display in alloy_display_map and alloy_display_map[display] != orig:
            display = f"{display} | {orig}"
        alloy_display_map[display] = orig
    display_alloys_sorted = sorted(list(alloy_display_map.keys()))

    with r1c2:
        if style_mode == "Individual":
            selected_alloy_displays = st.multiselect(
                "Choose alloys",
                options=display_alloys_sorted,
                default=[],
                key="dos_alloys_multi",
            )
        else:
            df_fam_src = df_master.copy()
            if selected_users:
                df_fam_src = df_fam_src[df_fam_src["user"].isin(selected_users)]
            fam_series = df_fam_src["FamilyKey"].replace("", np.nan).dropna()
            fam_counts = fam_series.value_counts()
            families_all = fam_counts.index.tolist()
            selected_family = st.multiselect(
                "Choose families",
                options=families_all,
                default=[],
                key="dos_families_multi",
            )

    # Compact row: left = TDOS/PDOS checkboxes, right = global line width (50% each)
    row_td_pd, row_linew = st.columns([1, 1], gap="small")
    with row_td_pd:
        c1, c2 = st.columns([1, 1], gap="small")
        with c1:
            show_tdos = st.checkbox("TDOS", value=True, key="dos_show_tdos")
        with c2:
            show_pdos = st.checkbox("PDOS", value=False, key="dos_show_pdos")
        if show_pdos:
            st.markdown("PDOS orbitals", unsafe_allow_html=True)
            o1, o2, o3, o4 = st.columns(4, gap="small")
            with o1:
                orb_s = st.checkbox("s", False, key="orb_s")
            with o2:
                orb_p = st.checkbox("p", False, key="orb_p")
            with o3:
                orb_t2g = st.checkbox("t2g", True, key="orb_t2g")
            with o4:
                orb_eg = st.checkbox("eg", False, key="orb_eg")
        else:
            orb_s = orb_p = orb_t2g = orb_eg = False

    with row_linew:
        st.markdown("<div class='card-label'>Global line width (applies to TDOS & PDOS)</div>", unsafe_allow_html=True)
        global_line_width = st.slider("", 1, 8, 2, key="global_line_width")

    # Axis limits (compact)
    ax1, ax2, ax3, ax4 = st.columns(4, gap="small")
    with ax1:
        xmin = st.number_input("Xmin", -50.0, 50.0, -8.0, key="dos_xmin")
    with ax2:
        xmax = st.number_input("Xmax", -50.0, 50.0, 4.0, key="dos_xmax")
    with ax3:
        ymin = st.number_input("Ymin", 0.0, 100.0, 0.0, key="dos_ymin")
    with ax4:
        ymax = st.number_input("Ymax", 0.0, 100.0, 2.5, key="dos_ymax")

    # Styling controls (cards) — pagination
    st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
    st.markdown("**Styling controls**", unsafe_allow_html=True)

    if "dos_card_map" not in st.session_state:
        st.session_state["dos_card_map"] = {}
    if "dos_card_page" not in st.session_state:
        st.session_state["dos_card_page"] = 0

    tiles_full_list = []
    family_color_mode = None
    if style_mode == "Individual":
        tiles_full_list = [alloy_display_map[d] for d in (selected_alloy_displays or [])]
    else:
        family_color_mode = st.radio(
            "Coloring mode",
            ["Family coloring", "Individual coloring"],
            index=0,
            key="dos_family_color_mode",
        )
        selected_families = (selected_family or [])
        if family_color_mode == "Family coloring":
            tiles_full_list = selected_families
        else:
            df_tmp = df_master.copy()
            if selected_users:
                df_tmp = df_tmp[df_tmp["user"].isin(selected_users)]
            df_tmp = df_tmp[df_tmp["FamilyKey"].isin(selected_families)]
            tiles_full_list = df_tmp["alloy"].drop_duplicates().tolist()

    # ensure deterministic default mapping exists for each tile key
    for key_item in tiles_full_list:
        if key_item not in st.session_state["dos_card_map"]:
            tcol, pcol = two_distinct_colors(str(key_item))
            st.session_state["dos_card_map"][key_item] = {
                "tdos_color": tcol,
                "pdos_color": pcol,
                "line_style": "solid",
            }

    # pager and render cards (4 per page)
    PAGE_SIZE = 4
    total_tiles = len(tiles_full_list)
    page = st.session_state["dos_card_page"]
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, total_tiles)
    pcol1, pcol2, pcol3 = st.columns([3, 6, 3])
    with pcol1:
        if st.button("Prev Page ", key="dos_prev"):
            st.session_state["dos_card_page"] = max(0, st.session_state["dos_card_page"] - 1)
    with pcol3:
        if st.button("Next Page ", key="dos_next", icon_position="right"):
            if end < total_tiles:
                st.session_state["dos_card_page"] += 1

    visible_tiles = tiles_full_list[start:end]

    # Card rendering
    if visible_tiles:
        cols = st.columns(len(visible_tiles), gap="small")
        for col_widget, key_item in zip(cols, visible_tiles):
            with col_widget:
                title = alloy_unicode_title(key_item) if (
                    style_mode == "Individual"
                    or (style_mode == "Family" and family_color_mode == "Individual coloring")
                ) else str(key_item)
                st.markdown(
                    f"<div class='family-card'><div class='family-card-title'>{title}</div></div>",
                    unsafe_allow_html=True,
                )

                # ensure entry exists
                if key_item not in st.session_state["dos_card_map"]:
                    tcol, pcol = two_distinct_colors(str(key_item))
                    st.session_state["dos_card_map"][key_item] = {
                        "tdos_color": tcol,
                        "pdos_color": pcol,
                        "line_style": "solid",
                    }

                entry = st.session_state["dos_card_map"][key_item]

                # Row 1: labels and color pickers
                st.markdown("<div style='display:flex; gap:8px;'>", unsafe_allow_html=True)
                cc1, cc2 = st.columns([1, 1], gap="small")
                with cc1:
                    st.markdown("<div class='card-label'>TDOS color</div>", unsafe_allow_html=True)
                    c_t = st.color_picker("", value=entry["tdos_color"], key=f"tdos_color__{safe_key(key_item)}")
                    entry["tdos_color"] = c_t
                with cc2:
                    st.markdown("<div class='card-label'>PDOS color</div>", unsafe_allow_html=True)
                    c_p = st.color_picker("", value=entry["pdos_color"], key=f"pdos_color__{safe_key(key_item)}")
                    entry["pdos_color"] = c_p
                st.markdown("</div>", unsafe_allow_html=True)

                # Row 2: Line style dropdown (single control) — full width
                st.markdown("<div class='card-label'>Line style</div>", unsafe_allow_html=True)

                style_options_display = ["Solid", "Dot", "Dash", "DashDot"]
                style_map_lower_to_plot = {"solid": "solid", "dot": "dot", "dash": "dash", "dashdot": "dashdot"}
                current_style = entry.get("line_style", "solid") or "solid"
                index_choice = 0
                for i, disp in enumerate(style_options_display):
                    if style_map_lower_to_plot.get(disp.lower()) == current_style.lower():
                        index_choice = i
                        break
                selected_disp = st.selectbox(
                    "",
                    style_options_display,
                    index=index_choice,
                    key=f"line_style__{safe_key(key_item)}",
                )
                entry["line_style"] = style_map_lower_to_plot[selected_disp.lower()]
                st.session_state["dos_card_map"][key_item] = entry
    else:
        st.info("No styling items to show. Select users and alloys/families.")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Plot (left column)
# ---------------------------
with col_plot:
    fig = go.Figure()

    # compute n_selected for height
    if style_mode == "Individual":
        n_selected = len(selected_alloy_displays or [])
    else:
        n_selected = len(selected_family or []) if "selected_family" in locals() else 0
    fig_height = get_plot_height_for_mode(style_mode, n_selected)

    plot_bg = "#262e40"
    fig.update_layout(
        plot_bgcolor=plot_bg,
        paper_bgcolor=plot_bg,
        height=fig_height,
        legend=dict(
            x=0.02,
            y=0.98,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(color="#ffffff"),
        ),
        margin=dict(l=40, r=20, t=30, b=40),
    )

    fig.update_xaxes(
        title_text="Energy (eV)",
        range=[xmin, xmax],
        showgrid=False,
        showline=True,
        linecolor="#ffffff",
        tickfont=dict(size=12, color="#ffffff"),
        title_font=dict(size=14, color="#ffffff"),
    )
    fig.update_yaxes(
        title_text="DOS per Atom",
        range=[ymin, ymax],
        showgrid=False,
        showline=True,
        linecolor="#ffffff",
        tickfont=dict(size=12, color="#ffffff"),
        title_font=dict(size=14, color="#ffffff"),
    )

    # prepare df filtered by users
    df_plot_src = df_master.copy()
    if selected_users:
        df_plot_src = df_plot_src[df_plot_src["user"].isin(selected_users)]

    # select alloys to plot
    if style_mode == "Individual":
        alloys_to_plot = [alloy_display_map[d] for d in (selected_alloy_displays or [])]
    else:
        sel_fams = (selected_family or [])
        if sel_fams:
            df_tmp = df_plot_src[df_plot_src["FamilyKey"].isin(sel_fams)]
            alloys_to_plot = df_tmp["alloy"].drop_duplicates().tolist()
        else:
            alloys_to_plot = []

    # Plot each alloy; family coloring uses family map entry
    for alloy in alloys_to_plot:
        df_row = df_plot_src[df_plot_src["alloy"] == alloy]
        if df_row.empty:
            continue
        row = df_row.iloc[0]
        uid = row.get("unique_id", None)
        atoms = row.get("atom_count", 1) or 1
        fam = row.get("FamilyKey", "")

        # resolve entry priority
        entry = None
        if style_mode == "Family" and family_color_mode == "Family coloring":
            entry = st.session_state["dos_card_map"].get(fam, None)
        if entry is None:
            entry = st.session_state["dos_card_map"].get(alloy, None)
        if entry is None:
            t, p = two_distinct_colors(alloy)
            entry = {"tdos_color": t, "pdos_color": p, "line_style": "solid"}

        tdos_color = entry.get("tdos_color")
        pdos_color = entry.get("pdos_color")
        style_dash = entry.get("line_style", "solid")
        width = global_line_width  # global slider controls widths now

        tdos_path = os.path.join("data", "tdos", str(uid))
        pdos_path = os.path.join("data", "pdos", str(uid))

        # TDOS trace
        if show_tdos and uid is not None and os.path.exists(tdos_path):
            try:
                E, D = load_tdos(tdos_path)
                D = D / float(atoms)
                D = smooth_dos(E, D, sigma_ev)
                interp = interp1d(E, D, fill_value="extrapolate")
                nef = float(interp(0))
                name_label = f"{alloy_unicode_title(alloy)} (N(Ef)={nef:.2f})"
                hovertemplate = "<b>%{text}</b><br>N(Ef)=%{meta:.4g}<br>Energy=%{x:.4g}<br>DOS=%{y:.4g}<extra></extra>"
                fig.add_trace(go.Scatter(
                    x=E, y=D, mode="lines", name=name_label,
                    line=dict(color=tdos_color, width=width, dash=style_dash),
                    text=[name_label] * len(E), meta=[nef] * len(E), hovertemplate=hovertemplate
                ))
            except Exception as e:
                st.warning(f"Failed to load TDOS for {alloy}: {e}")

        # PDOS trace
        if show_pdos and uid is not None and os.path.exists(pdos_path):
            try:
                df_pdos = load_pdos(pdos_path)
                energy = df_pdos.iloc[:, 0]
                cols = df_pdos.columns[1:]
                s_cols = [c for c in cols if "_s" in c]
                p_cols = [c for c in cols if "_p" in c]
                t2g_cols = [c for c in cols if any(x in c for x in ["dxy", "dyz", "dxz"])]
                eg_cols = [c for c in cols if any(x in c for x in ["dz2", "dx2"])]
                total = np.zeros(len(energy))
                if orb_s:
                    total += df_pdos[s_cols].sum(axis=1) if s_cols else 0
                if orb_p:
                    total += df_pdos[p_cols].sum(axis=1) if p_cols else 0
                if orb_t2g:
                    total += df_pdos[t2g_cols].sum(axis=1) if t2g_cols else 0
                if orb_eg:
                    total += df_pdos[eg_cols].sum(axis=1) if eg_cols else 0

                total = total / float(atoms)
                total = smooth_dos(energy, total, sigma_ev)

                try:
                    nef_p = float(interp1d(energy, total, fill_value="extrapolate")(0))
                except Exception:
                    nef_p = np.nan
                name_label = f"{alloy_unicode_title(alloy)} (PDOS N(Ef)={nef_p:.2f})"
                hovertemplate = "<b>%{text}</b><br>N(Ef)=%{meta:.4g}<br>Energy=%{x:.4g}<br>PDOS=%{y:.4g}<extra></extra>"
                fig.add_trace(go.Scatter(
                    x=energy, y=total, mode="lines", name=name_label,
                    line=dict(color=pdos_color, width=width, dash=style_dash),
                    text=[name_label] * len(energy), meta=[nef_p] * len(energy), hovertemplate=hovertemplate
                ))
            except Exception as e:
                st.warning(f"Failed to load PDOS for {alloy}: {e}")

    # Fermi line
    if alloys_to_plot:
        fig.add_vline(x=0, line_dash="dash", line_color="#ffffff", opacity=0.6)

    fig.update_layout(legend=dict(font=dict(color="#ffffff")))
    st.plotly_chart(fig, width="stretch")


















# =====================================================
# DISPLAY DATAFRAME (ALL COLUMNS)
# =====================================================
st.markdown('<div class="details-dataframe-section">', unsafe_allow_html=True)
st.subheader("📋 Full Dataset")

display_df = pd.json_normalize(filtered_df.to_dict("records"), sep=".")
column_config = {}
for column_name in display_df.columns:
    display_label = column_name.replace("_", " ").replace(".", " / ")
    display_label = re.sub(r"\s+", " ", display_label).strip().title()
    display_label = display_label.replace("Id", "ID")
    column_config[column_name] = st.column_config.Column(display_label)

st.dataframe(
    display_df,
    width="stretch",
    column_config=column_config,
)
st.markdown('</div>', unsafe_allow_html=True)








# =====================================================
# OPTIONAL: BACK BUTTON
# =====================================================
if st.button("← Back to Dashboard", key="details_back_button"):
    st.switch_page("pages/research/rhea-dft-data/overview.py")

st.markdown('</div>', unsafe_allow_html=True)
