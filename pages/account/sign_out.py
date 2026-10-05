import streamlit as st

from codhem.services.auth_service import is_authenticated, sign_out


st.title("Sign Out")
st.caption(
    'Choose Sign Out below to end your current CODHEM session. Sign in again with Google '
    'when you want to return to the database, research dashboards, or models.'
)

if not is_authenticated():
    st.info("You are already signed out.")
    st.page_link(
        "pages/account/sign_in.py",
        label="Go to sign in",
        icon=":material/login:",
    )
    st.stop()

st.write("Select the button below to sign out of CODHEM.")

if st.button("Sign Out", width="stretch", key="account-sign-out"):
    sign_out()
