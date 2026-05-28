import streamlit as st

from codhem.services.auth_service import get_current_user, is_authenticated, sign_out


st.title("Sign In")
st.caption("Sign in with Google to access CODHEM.")

if not is_authenticated():
    if st.button("Continue with Google", width="stretch", key="google-login"):
        st.login("google")
else:
    current_user = get_current_user()
    st.success(f"Signed in as {st.user.get('email', '')}.")
    if current_user is None:
        st.page_link(
            "pages/account/complete_registration.py",
            label="Complete registration",
            icon=":material/person_add:",
        )
    elif not current_user.verified:
        st.info(
            "Your registration has been submitted. An administrator must verify your account before you can access the site."
        )
    else:
        st.caption(
            f"Role: {current_user.role} | Organization: {current_user.organization}"
        )

    if st.button("Sign Out", width="stretch", key="google-logout"):
        sign_out()
