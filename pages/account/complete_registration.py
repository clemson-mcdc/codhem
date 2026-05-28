import streamlit as st

from codhem.services.auth_service import (
    get_current_identity_email,
    get_current_identity_name,
    get_current_user,
    is_authenticated,
    register_current_user,
    sign_out,
)


st.title("Complete Registration")
st.caption("Finish creating your CODHEM profile.")

if not is_authenticated():
    st.switch_page("pages/account/sign_in.py")
    st.stop()

current_user = get_current_user()
if current_user is not None:
    if current_user.verified:
        st.success("Your CODHEM profile is complete.")
        st.caption("Use the sidebar to continue into the application.")
    else:
        st.info(
            "Your registration has been submitted. An administrator must verify your account before you can access the site."
        )
    st.stop()

st.write("Complete your CODHEM profile to submit your access request.")

position_options = [
    "Student",
    "Researcher",
    "Professor",
    "Private Sector Employee",
    "Other",
]

with st.form("complete-registration-form"):
    name = st.text_input("Full Name", value=get_current_identity_name())
    st.text_input("Email", value=get_current_identity_email(), disabled=True)
    organization = st.text_input("Organization")
    country = st.text_input("Country")
    position = st.selectbox("Position", position_options)
    submitted = st.form_submit_button("Complete Registration", width="stretch")

if submitted:
    success, message = register_current_user(name, organization, country, position)
    if success:
        st.success(message)
        st.rerun()
    else:
        st.error(message)

st.divider()
if st.button("Sign Out", width="stretch", key="complete-registration-sign-out"):
    sign_out()
