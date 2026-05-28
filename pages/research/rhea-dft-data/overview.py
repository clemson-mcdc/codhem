from functools import partial
import os
import re
import zipfile
from io import BytesIO

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from codhem.components.periodic_table import ELEMENTS, render_periodic_table
from codhem.services.auth_service import require_registered_user
from codhem.services.dft_calculations_service import build_dft_calculations_dashboard_dataframe


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
# LOAD CSS
# =====================================================
def load_css():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, "styles.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# =====================================================
# TITLE
# =====================================================
st.title("⚛️ DFT Calculation Dashboard for High Entropy Alloys ")
st.caption("A Structured Computational Repository of Alloy Properties")

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():
    return build_dft_calculations_dashboard_dataframe()


df = load_data()
df["shear_modulus_average"] = df["shear_modulus"].apply(
    lambda values: values.get("average") if isinstance(values, dict) else None
)
df["youngs_modulus_e_vrh"] = df["youngs_modulus"].apply(
    lambda values: values.get("e_vrh") if isinstance(values, dict) else None
)

# =====================================================
# ELEMENT DEFINITIONS
# =====================================================
elements = [element["symbol"] for element in ELEMENTS]
present_cols = [f"{el}_present" for el in elements]

# Color map for alloy complexity (same as pie chart)
complexity_color_map = {
    "Pure": "#4CAF50",
    "Binary": "#2196F3",
    "Ternary": "#FFC107",
    "Quaternary": "#E4507D",
    "Quinary": "#67B651",
    ">5 elements": "#9C27B0"
}

elastic_completed = df["has_elastic"]
completed_df = df[elastic_completed].copy()

# =====================================================
# METRICS (CUSTOM HTML + STREAMLIT NAV)
# =====================================================
st.markdown('<div class="metric-row">', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
        <div class="metric-card-wrapper">
            <div class="custom-metric">
                <div class="metric-label">🧮 Total calculations</div>
                <div class="metric-value">{len(df)}</div>
            </div>
            <div class="metric-button-container">
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/research/rhea-dft-data/total_calculations.py", label="View details\u00A0\u00A0 →")
    st.markdown("</div></div>", unsafe_allow_html=True)

with c2:
    st.markdown(
        f"""
        <div class="metric-card-wrapper">
            <div class="custom-metric">
                <div class="metric-label">✅  Elastic Tensor & DOS </div>
                <div class="metric-value">{int(elastic_completed.sum())}</div>
            </div>
            <div class="metric-button-container">
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/research/rhea-dft-data/completed_elastic.py", label="View details \u00A0\u00A0 →")
    st.markdown("</div></div>", unsafe_allow_html=True)

with c3:
    st.markdown(
        f"""
        <div class="metric-card-wrapper">
            <div class="custom-metric">
                <div class="metric-label">⚠️ Only DOS</div>
                <div class="metric-value">{int((~elastic_completed).sum())}</div>
            </div>
            <div class="metric-button-container">
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/research/rhea-dft-data/missing_elastic.py", label="View details\u00A0\u00A0  →")
    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# PLOTS
# =====================================================
col1, col2 = st.columns(2)

# ---------- ELEMENT OCCURRENCE ----------
with col1:
    st.subheader("🧬 Element Occurrence")

    total, elastic = {}, {}

    for col in present_cols:
        t = df[col].fillna(0).sum()
        e = completed_df[col].fillna(0).sum()
        if t > 0:
            el = col.replace("_present", "")
            total[el] = int(t)
            elastic[el] = int(e)

    element_df = pd.DataFrame({
        "Element": total.keys(),
        "Total": total.values(),
        "Elastic": elastic.values()
    }).sort_values("Total")

    fig = go.Figure()

    fig.add_bar(
        y=element_df["Element"],
        x=element_df["Total"],
        orientation="h",
        name="Total calculations",
        marker_color="#4273CE",
        # Add hover information
        hovertemplate="<span style='font-size:16px; color:#AAAAAA'><b>%{y}</b></span><br>" +
             "<span style='font-size:14px; color:#AAAAAA'>Total: <span style='color:#AAAAAA'>%{x}</span></span>" +
             "<extra></extra>"
    )

    fig.add_bar(
        y=element_df["Element"],
        x=element_df["Elastic"],
        orientation="h",
        name="Elastic tensor available",
        marker_color="#20BF65",
        # Add hover information
        hovertemplate="<span style='font-size:16px; color:#AAAAAA'><b>%{y}</b></span><br>" +
             "<span style='font-size:14px; color:#AAAAAA'>Total: <span style='color:#AAAAAA'>%{x}</span></span>" +
             "<extra></extra>"
    )

    fig.update_layout(
        barmode="overlay",
        template="plotly_dark",

        # IMPORTANT: transparent so card controls background
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",

        font=dict(size=14),
        xaxis=dict(
            title="Number of calculations",
            title_font=dict(size=16, color="#FFFFFF", weight=700),
            tickfont=dict(size=13),
            showgrid=True,
            gridcolor="#5f5f63",  # Very light vertical grid lines
            gridwidth=1,
            showline=True,  # Show axis line
            linecolor="#5f5f63",  # Axis line color
            linewidth=2,
            range=[-1, 340],
            tickmode="array",  # Use custom tick values
            tickvals=[0, 50, 100, 150, 200, 250, 300, 340],  # Custom tick positions
            ticktext=["0", "50", "100", "150", "200", "250", "300", "340"],
        ),
        yaxis=dict(
            title="Element",
            title_font=dict(size=16, color="#FFFFFF", weight=700),
            tickfont=dict(size=13)
        ),

        legend=dict(
            font=dict(size=16),
            bordercolor="#2a2f3a",
            borderwidth=0.5
        ),
        

        margin=dict(l=80, r=30, t=10, b=40),
        height=480,



        hoverlabel=dict(
            bgcolor="#1a1d29",  # Dark blue-gray background
            bordercolor="#5f5f63",  # Border color matching your axis lines
            font_size=14,
            font_color="white",
            font_family="Arial, sans-serif"
            
        ),
    )

    st.plotly_chart(fig, width="stretch")


# ---------- ALLOY COMPLEXITY ----------
with col2:
    st.subheader("🧩 Alloy Complexity")

    counts = df["complexity"].value_counts()

    fig = px.pie(
        names=counts.index,
        values=counts.values,
        hole=0.6,
        color=counts.index,
        color_discrete_map=complexity_color_map,
        template="plotly_dark"
    )

    fig.update_traces(
        textinfo="label+value",
        textfont_size=16,  # Increased from 14
        textfont_color="black",  # Added: set text color to white
        marker=dict(line=dict(color="white", width=1.5)),
        # Optional: improve hover text
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent:.1%}<extra></extra>"
    )

    # Update layout - remove legend and adjust fonts
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(
            size=16,  # Increased from 14
            color="Black",
            weight=700 
                # Added: set default font color to white
        ),
        # Remove legend completely
        showlegend=False,  # This is the key change
        # Keep the EXACT same height and margins
        height=480,
        margin=dict(l=40, r=40, t=10, b=40)
    )

    st.plotly_chart(fig, width="stretch")



# =====================================================
# NEW ROW FOR PLOTS 3 & 4
# =====================================================
st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
col3, col4 = st.columns(2)



with col3:
    st.subheader("📉 Modulus vs Ductility")

    # --------------------------------------------------
    # DATA PREPARATION
    # --------------------------------------------------
    plot3_df = completed_df.copy()
    available_complexities = sorted(plot3_df["complexity"].unique().tolist())
    ALL_TAG = "All"
    
    # Initialize session state for selection and widget key
    if "complexity_state_3" not in st.session_state:
        st.session_state.complexity_state_3 = available_complexities
    
    if "widget_key_3" not in st.session_state:
        st.session_state.widget_key_3 = 1000

    # --------------------------------------------------
    # CALLBACK LOGIC
    # --------------------------------------------------
    def sync_state_3():
        """Handles the logic when user interacts with the multiselect."""
        current_key = f"complexity_filter_multi_3_{st.session_state.widget_key_3}"
        ui_val = st.session_state[current_key]
        
        if ALL_TAG in ui_val:
            # User wants everything: Reset state and rotate key to refresh UI buttons
            st.session_state.complexity_state_3 = available_complexities
            st.session_state.widget_key_3 += 1
        elif not ui_val:
            # User cleared all: Keep it empty to allow selection from dropdown
            st.session_state.complexity_state_3 = []
        else:
            # Normal manual selection
            st.session_state.complexity_state_3 = [c for c in ui_val if c != ALL_TAG]

    # --------------------------------------------------
    # UI COMPONENTS (DROPDOWNS)
    # --------------------------------------------------
    dropdown_col1, dropdown_col2 = st.columns([1, 3])

    with dropdown_col1:
        st.markdown('<div class="dropdown-modulus">', unsafe_allow_html=True)
        modulus_options = {
            "Elastic": "youngs_modulus_e_vrh",
            "Bulk": "bulk_modulus",
            "Shear": "shear_modulus_average",
        }
        selected_modulus = st.selectbox(
            "Select Modulus Type:",
            options=list(modulus_options.keys()),
            key="modulus_selector_plot3_final"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with dropdown_col2:
        st.markdown('<div class="dropdown-complexity">', unsafe_allow_html=True)

        current_selection = st.session_state.complexity_state_3
        remaining = [c for c in available_complexities if c not in current_selection]
        
        # Determine dropdown list: Only show 'All' if 2 or more items are unselected
        if len(remaining) > 1:
            dropdown_options_list = [ALL_TAG] + remaining
        else:
            dropdown_options_list = remaining

        # Use the dynamic key to force a visual refresh when required
        dynamic_key = f"complexity_filter_multi_3_{st.session_state.widget_key_3}"

        st.multiselect(
            "Filter Complexity:",
            options=current_selection + dropdown_options_list,
            default=current_selection,
            key=dynamic_key,
            on_change=sync_state_3
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------
    # FINAL STATE & DATA FILTERING
    # --------------------------------------------------
    # Use the variable name expected by your downstream plotting code
    selected_complexities = [c for c in st.session_state.complexity_state_3 if c != ALL_TAG]

    y_col = modulus_options[selected_modulus]
    filtered_df = plot3_df[plot3_df["complexity"].isin(selected_complexities)].copy()





    # --------------------------------------------------
    # PLOT
    # --------------------------------------------------
    fig3 = go.Figure()

    for complexity in selected_complexities:
        complexity_df = filtered_df[filtered_df["complexity"] == complexity]

        if not complexity_df.empty and complexity in complexity_color_map:
            fig3.add_trace(go.Scatter(
                x=1 / complexity_df["pugh_ratio"].replace(0, np.nan),
                y=complexity_df[y_col],
                mode="markers",
                name=complexity,
                marker=dict(
                    size=10,
                    color=complexity_color_map[complexity],
                    line=dict(width=1, color="white")
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    f"{selected_modulus.split()[0]}: %{{y:.1f}} GPa<br>"
                    "Pugh Ratio: %{x:.2f}<br>"
                    "Complexity: %{customdata[0]}<extra></extra>"
                ),
                text=complexity_df["alloy"],
                customdata=complexity_df[["complexity"]].values
            ))

    # --------------------------------------------------
    # CHART STYLING
    # --------------------------------------------------
    y_title_map = {
        "youngs_modulus_e_vrh": "Elastic Modulus (Strength) [GPa]",
        "bulk_modulus": "Bulk Modulus [GPa]",
        "shear_modulus_average": "Shear Modulus [GPa]",
    }

    fig3.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14),
        xaxis=dict(
            title="1 / Pugh Ratio (Ductility)",
            title_font=dict(size=16, color="#FFFFFF", weight=700),
            tickfont=dict(size=13),
            showgrid=True,
            gridcolor="#5f5f63",
            gridwidth=1,
            showline=True,
            linecolor="#5f5f63",
            linewidth=2
        ),
        yaxis=dict(
            title=y_title_map[y_col],
            title_font=dict(size=16, color="#FFFFFF", weight=700),
            tickfont=dict(size=13),
            showgrid=True,
            gridcolor="#5f5f63",
            gridwidth=1,
            showline=True,
            linecolor="#5f5f63",
            linewidth=2
        ),
        legend=dict(
            font=dict(size=14),
            title=dict(text="Alloy Complexity", font=dict(size=14, color="#FFFFFF"))
        ),
        margin=dict(l=80, r=30, t=40, b=40),
        height=480
    )

    # --------------------------------------------------
    # SUBTITLE
    # --------------------------------------------------
    subtitle_text = (
        "Active Filters: All"
        if len(selected_complexities) == len(available_complexities)
        else f"Active Filters: {', '.join(selected_complexities)}"
    )

    fig3.add_annotation(
        text=subtitle_text,
        xref="paper",
        yref="paper",
        x=0,
        y=1.08,
        showarrow=False,
        font=dict(size=12, color="#888888")
    )

    st.plotly_chart(fig3, width="stretch")

# ---------- PLOT 4: MODULUS VS NEF ----------
with col4:
    st.subheader("🔬 Modulus vs Nef")

    # --------------------------------------------------
    # DATA PREPARATION
    # --------------------------------------------------
    plot4_df = completed_df.copy()
    available_complexities_4 = sorted(plot4_df["complexity"].unique().tolist())
    ALL_TAG = "All"

    # Initialize session state for Plot 4
    if "complexity_state_4" not in st.session_state:
        st.session_state.complexity_state_4 = available_complexities_4
    
    if "widget_key_4" not in st.session_state:
        st.session_state.widget_key_4 = 4000  # Unique starting key for Plot 4

    # --------------------------------------------------
    # CALLBACK LOGIC
    # --------------------------------------------------
    def sync_state_4():
        """Handles logic for Plot 4 multiselect."""
        current_key = f"complexity_filter_multi_4_{st.session_state.widget_key_4}"
        ui_val = st.session_state[current_key]
        
        if ALL_TAG in ui_val:
            # Reset to all and rotate key to force buttons to reappear
            st.session_state.complexity_state_4 = available_complexities_4
            st.session_state.widget_key_4 += 1
        elif not ui_val:
            # Allow empty state
            st.session_state.complexity_state_4 = []
        else:
            # Sync selection, filtering out the 'All' tag
            st.session_state.complexity_state_4 = [c for c in ui_val if c != ALL_TAG]

    # --------------------------------------------------
    # DROPDOWNS (25% / 75%)
    # --------------------------------------------------
    dropdown_col1, dropdown_col2 = st.columns([1, 3])

    with dropdown_col1:
        st.markdown('<div class="dropdown-modulus">', unsafe_allow_html=True)
        # Assuming modulus_options dictionary is defined globally as in Plot 3
        selected_modulus_2 = st.selectbox(
            "Select Modulus Type:",
            options=list(modulus_options.keys()),
            index=0,
            key="modulus_selector_plot4_final"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with dropdown_col2:
        st.markdown('<div class="dropdown-complexity">', unsafe_allow_html=True)
        
        current_selection_4 = st.session_state.complexity_state_4
        remaining_4 = [c for c in available_complexities_4 if c not in current_selection_4]

        # Dropdown list logic: Show 'All' if 2 or more are unselected
        if len(remaining_4) > 1:
            dropdown_options_list_4 = [ALL_TAG] + remaining_4
        else:
            dropdown_options_list_4 = remaining_4

        # Dynamic key to force visual refresh
        dynamic_key_4 = f"complexity_filter_multi_4_{st.session_state.widget_key_4}"

        st.multiselect(
            "Filter Complexity:",
            options=current_selection_4 + dropdown_options_list_4,
            default=current_selection_4,
            key=dynamic_key_4,
            on_change=sync_state_4
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------
    # FINAL STATE & DATA FILTERING
    # --------------------------------------------------
    # Extract the actual list for filtering (stripping ALL_TAG if present)
    selected_complexities_4 = [c for c in st.session_state.complexity_state_4 if c != ALL_TAG]

    y_col_2 = modulus_options[selected_modulus_2]
    filtered_df_4 = plot4_df[
        plot4_df["complexity"].isin(selected_complexities_4)
    ].copy()
    # --------------------------------------------------
    # PLOT
    # --------------------------------------------------
    fig4 = go.Figure()

    for complexity in selected_complexities_4:
        complexity_df = filtered_df_4[
            filtered_df_4["complexity"] == complexity
        ]

        if not complexity_df.empty and complexity in complexity_color_map:
            fig4.add_trace(go.Scatter(
                x=complexity_df["dos_at_fermi"].apply(
                    lambda values: values.get("total") if isinstance(values, dict) else None
                ),
                y=complexity_df[y_col_2],
                mode="markers",
                name=complexity,
                marker=dict(
                    size=10,
                    color=complexity_color_map[complexity],
                    line=dict(width=1, color="white")
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    f"{selected_modulus_2.split()[0]}: %{{y:.1f}} GPa<br>"
                    "N<sub>ef</sub>: %{x:.2f} states/eV/atom<br>"
                    "Complexity: %{customdata[0]}<extra></extra>"
                ),
                text=complexity_df["alloy"],
                customdata=complexity_df[["complexity"]].values
            ))

    # --------------------------------------------------
    # CHART STYLING
    # --------------------------------------------------
    y_title_map_2 = {
        "youngs_modulus_e_vrh": "Elastic Modulus (Strength) [GPa]",
        "bulk_modulus": "Bulk Modulus [GPa]",
        "shear_modulus_average": "Shear Modulus [GPa]",
    }

    fig4.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14),
        xaxis=dict(
            title="N<sub>ef</sub> (states/eV/atom)",
            title_font=dict(size=16, color="#FFFFFF", weight=700),
            tickfont=dict(size=13),
            showgrid=True,
            gridcolor="#5f5f63",
            gridwidth=1,
            showline=True,
            linecolor="#5f5f63",
            linewidth=2
        ),
        yaxis=dict(
            title=y_title_map_2[y_col_2],
            title_font=dict(size=16, color="#FFFFFF", weight=700),
            tickfont=dict(size=13),
            showgrid=True,
            gridcolor="#5f5f63",
            gridwidth=1,
            showline=True,
            linecolor="#5f5f63",
            linewidth=2
        ),
        legend=dict(
            font=dict(size=14),
           
            title=dict(text="Alloy Complexity", font=dict(size=14, color="#FFFFFF"))
        ),
        margin=dict(l=80, r=30, t=40, b=40),
        height=480
    )

    # --------------------------------------------------
    # SUBTITLE
    # --------------------------------------------------
    subtitle_text_4 = (
        "Active Filters: All"
        if len(selected_complexities_4) == len(available_complexities_4)
        else f"Active Filters: {', '.join(selected_complexities_4)}"
    )

    fig4.add_annotation(
        text=subtitle_text_4,
        xref="paper",
        yref="paper",
        x=0,
        y=1.08,
        showarrow=False,
        font=dict(size=12, color="#888888")
    )

    st.plotly_chart(fig4, width="stretch")




























# =====================================================
# INTERACTIVE PERIODIC TABLE - FORM APPROACH
# =====================================================

# Initialize session state FIRST
if "selected_elements" not in st.session_state:
    st.session_state.selected_elements = []

st.divider()
st.header("🏗️ Filter Alloy Based on Element Selection")
present_elements = list(total.keys())


def toggle_selected_element(symbol):
    if symbol in st.session_state.selected_elements:
        st.session_state.selected_elements.remove(symbol)
    else:
        st.session_state.selected_elements.append(symbol)


render_periodic_table(
    on_element_click=toggle_selected_element,
    selected_symbols=st.session_state.selected_elements,
    available_symbols=present_elements,
    key_prefix="rhea-dft-data-periodic-table",
)

selected_text = ", ".join(st.session_state.selected_elements) if st.session_state.selected_elements else "<i>None</i>"
html_content = f"""
<div class="outer-center">
    <div class="inner-left">Selected Elements</div>
    <div class="inner-right">{selected_text}</div>
</div>
"""
st.markdown(html_content, unsafe_allow_html=True)

if st.button("Clear All Selections", key="clear_periodic", type="secondary"):
    st.session_state.selected_elements = []
    st.rerun()


# ============================================================
# FILTER ALLOYS (STRICT: MUST CONTAIN ALL SELECTED ELEMENTS)
# ============================================================

st.divider()

sel = st.session_state.selected_elements

# Only keep elements that actually have a _present column
valid_sel = [el for el in sel if f"{el}_present" in df.columns]

if valid_sel:
    # Start with full dataframe
    filtered_df = df.copy()

    # ALL selected elements must be present (AND condition)
    for el in valid_sel:
        filtered_df = filtered_df[filtered_df[f"{el}_present"] == 1]
else:
    # No valid selection → no alloys
    filtered_df = pd.DataFrame(columns=df.columns)
# ============================================================
# Base folder where your data folders are stored
# ============================================================
data_root = os.path.join(os.getcwd(), "data")



# Check subfolders
expected_folders = ["contcar", "pdos", "tdos"]
for folder in expected_folders:
    folder_path = os.path.join(data_root, folder)
    if not os.path.exists(folder_path):
        st.warning(f"⚠️ DEBUG: Folder missing → {folder_path}")


def get_data_file_map(unique_id):
    return {
        "contcar": unique_id,
        "pdos": unique_id,
        "tdos": unique_id,
    }

# ============================================================
# Download helpers for filtered alloys
# ============================================================
def make_safe_zip_name(value):
    safe = re.sub(r'[\\/:*?"<>|]+', "_", str(value).strip())
    safe = re.sub(r"\s+", "_", safe)
    return safe.strip("._") or "unknown"


@st.cache_data(show_spinner=False)
def create_filtered_alloys_zip_bytes(filtered_alloys):
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for unique_id, alloy_name in filtered_alloys:
            if not unique_id or str(unique_id) == "nan":
                continue

            for folder, filename in get_data_file_map(unique_id).items():
                src_path = os.path.join(data_root, folder, filename)
                if not os.path.exists(src_path):
                    continue

                safe_unique_id = make_safe_zip_name(unique_id)
                safe_alloy_name = make_safe_zip_name(alloy_name)
                new_name = f"{safe_alloy_name}_{safe_unique_id}"
                zipf.write(src_path, arcname=f"{folder}/{new_name}")

    buffer.seek(0)
    return buffer.getvalue()


def build_filtered_alloys_table(filtered_df):
    table_df = filtered_df[
        [
            "alloy",
            "atom_count",
            "structure",
            "potcar",
            "vol_per_atom",
            "bulk_modulus",
            "poisson_ratio",
            "pugh_ratio",
        ]
    ].copy()
    table_df["dos_at_fermi_total"] = filtered_df["dos_at_fermi"].apply(
        lambda values: values.get("total") if isinstance(values, dict) else None
    )
    table_df["shear_modulus_average"] = filtered_df["shear_modulus"].apply(
        lambda values: values.get("average") if isinstance(values, dict) else None
    )
    table_df["youngs_modulus_e_vrh"] = filtered_df["youngs_modulus"].apply(
        lambda values: values.get("e_vrh") if isinstance(values, dict) else None
    )
    return table_df.rename(
        columns={
            "alloy": "Alloy",
            "atom_count": "Atom Count",
            "structure": "Structure (OVITO)",
            "potcar": "POTCAR Used",
            "vol_per_atom": "Vol. per Atom",
            "dos_at_fermi_total": "DOS at Ef",
            "bulk_modulus": "Bulk Modulus (GPa)",
            "shear_modulus_average": "Shear Modulus (GPa)",
            "youngs_modulus_e_vrh": "Elastic Modulus (GPa)",
            "poisson_ratio": "Poisson Ratio",
            "pugh_ratio": "Pugh Ratio",
        }
    )


@st.fragment
def render_filtered_alloys_grid(filtered_df):
    st.subheader("Filtered Alloys")

    st.session_state["filtered_df"] = filtered_df.copy()

    if filtered_df.empty:
        st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
        st.info("No alloys available for selected elements.")
        return

    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

    table_df = build_filtered_alloys_table(filtered_df)
    unique_ids = filtered_df["unique_id"].reset_index(drop=True)
    dataframe_event = st.dataframe(
        table_df,
        key="filtered_alloys_grid",
        hide_index=False,
        width="stretch",
        height=520,
        on_select="rerun",
        selection_mode="multi-row",
        column_config={
            "Alloy": st.column_config.TextColumn(width="small"),
            "Atom Count": st.column_config.NumberColumn(width="small"),
            "Structure (OVITO)": st.column_config.TextColumn(width="small"),
            "POTCAR Used": st.column_config.TextColumn(width="large"),
            "Vol. per Atom": st.column_config.NumberColumn(format="%.3f", width="small"),
            "DOS at Ef": st.column_config.NumberColumn(format="%.3f", width="small"),
            "Bulk Modulus (GPa)": st.column_config.NumberColumn(format="%.3f", width="small"),
            "Shear Modulus (GPa)": st.column_config.NumberColumn(format="%.3f", width="small"),
            "Elastic Modulus (GPa)": st.column_config.NumberColumn(format="%.3f", width="small"),
            "Poisson Ratio": st.column_config.NumberColumn(format="%.3f", width="small"),
            "Pugh Ratio": st.column_config.NumberColumn(format="%.3f", width="small"),
        },
    )

    st.caption(f"Found {len(filtered_df)} results from the applied filters")

    selected_rows = dataframe_event.selection["rows"]
    selected_table_df = table_df.iloc[selected_rows] if selected_rows else table_df.iloc[0:0]
    selected_alloys = tuple(
        (str(unique_ids.iloc[row_index]), str(selected_table_df.iloc[position]["Alloy"]))
        for position, row_index in enumerate(selected_rows)
    )
    selection_count = len(selected_alloys)
    selected_zip_name = "Selected_Alloy_Data.zip"

    with st.container(horizontal=True, horizontal_alignment="left", vertical_alignment="center"):
        if st.button(
            "📊 Detailed Analysis",
            key="btn_details",
        ):
            st.switch_page("pages/research/rhea-dft-data/details.py")

        st.download_button(
            label="⬇ Download CSV",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="Filtered_Alloys.csv",
            mime="text/csv",
            key="btn_csv",
            on_click="ignore",
        )

        st.download_button(
            label="⬇ Download CONTCAR & DOS",
            data=partial(create_filtered_alloys_zip_bytes, selected_alloys),
            file_name=selected_zip_name,
            mime="application/zip",
            key="download_selected_alloys",
            on_click="ignore",
            disabled=selection_count == 0,
        )


render_filtered_alloys_grid(filtered_df)
