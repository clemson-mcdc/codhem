import streamlit as st

from codhem.services.auth_service import is_authenticated, sign_out


st.title("Sign Out")
st.caption("End your current CODHEM session.")

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
