from pathlib import Path

import streamlit as st

from codhem.components.layout import render_footer
from codhem.services.auth_service import (
    get_current_user,
    get_current_user_role,
    is_authenticated,
    is_verified_user,
)
from codhem.services.data_service import get_database_statistics

ROOT_DIR = Path(__file__).resolve().parent


def render_home_page():
    st.title("CODHEM")
    st.caption("Consolidated Database of High Entropy Materials")

    if is_authenticated():
        current_user = get_current_user()
        if current_user is None:
            st.divider()
            st.subheader("Complete Your Registration")
            st.write("Complete your CODHEM profile to submit your access request.")
            st.page_link(
                "pages/account/complete_registration.py",
                label="Open registration",
                icon=":material/person_add:",
            )
        elif not current_user.verified:
            st.divider()
            st.subheader("Verification Pending")
            st.write(
                "Your registration has been submitted. An administrator must verify your account before you can access the site."
            )
    else:
        st.page_link(
            "pages/account/sign_in.py",
            label="Sign In",
            icon=":material/login:",
        )

    st.divider()
    st.subheader("Scientific Data Access")
    st.write(
        "Browse curated high-entropy materials data through a structured material database interface."
    )

    st.divider()
    st.subheader("Database Exploration")
    st.write(
        "Filter compositions, inspect material properties, and review records in a searchable table."
    )

    st.divider()
    st.subheader("Machine Learning Models")
    st.write(
        "Open model pages, provide inputs, and inspect outputs for research models."
    )

    st.divider()
    st.subheader("MCDC Research")
    st.write(
        "Open member dashboards that package recurring research calculations into focused views."
    )


def render_dashboard_page():
    stats = get_database_statistics()

    st.title("CODHEM")
    st.caption("Consolidated Database of High Entropy Materials")

    st.subheader("Database Statistics")
    st.caption("Visualizing data from the High Entropy Materials Database")

    metric_col_1, metric_col_2 = st.columns(2)
    metric_col_1.metric("Total compositions", stats.total_compositions)
    metric_col_2.metric("Total DOIs", stats.total_dois)

    chart_col_1, chart_col_2 = st.columns(2)
    with chart_col_1:
        st.markdown("**Element distribution**")
        st.vega_lite_chart(
            {
                "data": {"values": stats.element_distribution},
                "mark": {"type": "arc", "innerRadius": 45},
                "encoding": {
                    "theta": {"field": "count", "type": "quantitative"},
                    "color": {"field": "label", "type": "nominal", "title": "Element"},
                    "tooltip": [
                        {"field": "label", "type": "nominal", "title": "Element"},
                        {"field": "count", "type": "quantitative", "title": "Count"},
                    ],
                },
            },
            width="stretch",
        )

    with chart_col_2:
        st.markdown("**Phase distribution**")
        st.vega_lite_chart(
            {
                "data": {"values": stats.phase_distribution},
                "mark": {"type": "arc", "innerRadius": 45},
                "encoding": {
                    "theta": {"field": "count", "type": "quantitative"},
                    "color": {"field": "label", "type": "nominal", "title": "Phase"},
                    "tooltip": [
                        {"field": "label", "type": "nominal", "title": "Phase"},
                        {"field": "count", "type": "quantitative", "title": "Count"},
                    ],
                },
            },
            width="stretch",
        )

    st.markdown("**Element distribution in distinctive compositions**")
    st.vega_lite_chart(
        {
            "data": {"values": stats.distinctive_composition_distribution},
            "mark": {
                "type": "bar",
                "cornerRadiusTopLeft": 4,
                "cornerRadiusTopRight": 4,
            },
            "encoding": {
                "x": {"field": "label", "type": "nominal", "title": "Element"},
                "y": {"field": "count", "type": "quantitative", "title": "Count"},
                "color": {"field": "label", "type": "nominal", "legend": None},
                "tooltip": [
                    {"field": "label", "type": "nominal", "title": "Element"},
                    {"field": "count", "type": "quantitative", "title": "Count"},
                ],
            },
        },
        width="stretch",
    )


def main():
    st.set_page_config(
        page_title="codhem",
        page_icon=":material/science:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    home_page = st.Page(
        render_home_page,
        title="Home",
        icon=":material/home:",
        default=True,
    )
    dashboard_page = st.Page(
        render_dashboard_page,
        title="Dashboard",
        icon=":material/dashboard:",
        url_path="dashboard",
    )
    material_database_page = st.Page(
        ROOT_DIR / "pages" / "application" / "material_database.py",
        title="COD'HEM Database",
        icon=":material/table_view:",
        url_path="material-database",
    )
    models_page = st.Page(
        ROOT_DIR / "pages" / "ml_models" / "overview.py",
        title="ML Models",
        icon=":material/neurology:",
        url_path="ml-models",
    )
    rhea_mpnn_page = st.Page(
        ROOT_DIR / "pages" / "ml_models" / "rhea_mpnn.py",
        title="RHEA-DOS-E Predictor",
        icon=":material/tune:",
        url_path="ml-models-rhea-mpnn",
    )
    research_overview_page = st.Page(
        ROOT_DIR / "pages" / "research" / "overview.py",
        title="Overview",
        icon=":material/lab_profile:",
        url_path="research-overview",
    )
    research_rhea_dft_data_page = st.Page(
        ROOT_DIR / "pages" / "research" / "rhea-dft-data" / "overview.py",
        title="RHEA DFT Data",
        icon=":material/person:",
        url_path="research-rhea-dft-data",
    )
    research_rhea_dft_data_total_calculations_page = st.Page(
        ROOT_DIR / "pages" / "research" / "rhea-dft-data" / "total_calculations.py",
        title="RHEA DFT Data Total Calculations",
        icon=":material/table_chart:",
        url_path="research-rhea-dft-data-total-calculations",
        visibility="hidden",
    )
    research_rhea_dft_data_completed_elastic_page = st.Page(
        ROOT_DIR / "pages" / "research" / "rhea-dft-data" / "completed_elastic.py",
        title="RHEA DFT Data Completed Elastic",
        icon=":material/task_alt:",
        url_path="research-rhea-dft-data-completed-elastic",
        visibility="hidden",
    )
    research_rhea_dft_data_missing_elastic_page = st.Page(
        ROOT_DIR / "pages" / "research" / "rhea-dft-data" / "missing_elastic.py",
        title="RHEA DFT Data Missing Elastic",
        icon=":material/error_outline:",
        url_path="research-rhea-dft-data-missing-elastic",
        visibility="hidden",
    )
    research_rhea_dft_data_details_page = st.Page(
        ROOT_DIR / "pages" / "research" / "rhea-dft-data" / "details.py",
        title="RHEA DFT Data Details",
        icon=":material/analytics:",
        url_path="research-rhea-dft-data-details",
        visibility="hidden",
    )
    research_rhea_dft_data_duplicate_details_page = st.Page(
        ROOT_DIR / "pages" / "research" / "rhea-dft-data" / "duplicate_details.py",
        title="RHEA DFT Data Duplicate Details",
        icon=":material/content_copy:",
        url_path="research-rhea-dft-data-duplicate-details",
        visibility="hidden",
    )
    sign_in_page = st.Page(
        ROOT_DIR / "pages" / "account" / "sign_in.py",
        title="Sign In",
        icon=":material/login:",
        url_path="sign-in",
    )
    complete_registration_page = st.Page(
        ROOT_DIR / "pages" / "account" / "complete_registration.py",
        title="Complete Registration",
        icon=":material/person_add:",
        url_path="complete-registration",
    )
    profile_page = st.Page(
        ROOT_DIR / "pages" / "account" / "profile.py",
        title="Profile",
        icon=":material/account_circle:",
        url_path="profile",
    )
    sign_out_page = st.Page(
        ROOT_DIR / "pages" / "account" / "sign_out.py",
        title="Sign Out",
        icon=":material/logout:",
        url_path="sign-out",
    )
    users_page = st.Page(
        ROOT_DIR / "pages" / "administration" / "users.py",
        title="Users",
        icon=":material/group:",
        url_path="users",
    )

    if is_authenticated() and is_verified_user():
        navigation_pages = {
            "Application": [home_page, dashboard_page, material_database_page],
            "ML Models": [models_page, rhea_mpnn_page],
            "MCDC Research": [
                research_overview_page,
                research_rhea_dft_data_page,
                research_rhea_dft_data_total_calculations_page,
                research_rhea_dft_data_completed_elastic_page,
                research_rhea_dft_data_missing_elastic_page,
                research_rhea_dft_data_details_page,
                research_rhea_dft_data_duplicate_details_page,
            ],
            "Account": [profile_page, sign_out_page],
        }
        if get_current_user_role() == "Admin":
            navigation_pages["Administration"] = [users_page]
    elif is_authenticated():
        navigation_pages = {
            "Account": [profile_page, complete_registration_page, sign_out_page],
        }
    else:
        navigation_pages = {
            "Application": [home_page],
            "Account": [sign_in_page],
        }

    navigation = st.navigation(navigation_pages, position="sidebar")
    navigation.run()
    render_footer()


if __name__ == "__main__":
    main()
