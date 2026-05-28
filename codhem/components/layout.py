import streamlit as st


def render_navbar(pages: list):
    home_page, material_database_page, models_page = pages
    with st.container():
        brand_col, home_col, database_col, models_col = st.columns(
            [9, 1, 1.8, 1]
        )
        with brand_col:
            st.markdown("### CODHEM")
        with home_col:
            st.page_link(home_page, label="Home", icon=":material/home:")
        with database_col:
            st.page_link(
                material_database_page,
                label="Materials",
                icon=":material/table_view:",
            )
        with models_col:
            st.page_link(models_page, label="Models", icon=":material/neurology:")
    st.divider()


def render_footer():
    st.divider()
    st.caption("© 2026 MCDC Group, Clemson University.")
