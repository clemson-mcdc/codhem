import streamlit as st

from codhem.services.auth_service import (
    get_current_identity_email,
    get_current_identity_name,
    get_current_user,
    is_authenticated,
    update_current_user_profile,
)


st.title("Profile")
st.caption("View and update your CODHEM account details.")

if not is_authenticated():
    st.info("You need to sign in to view your profile.")
    st.page_link(
        "pages/account/sign_in.py",
        label="Go to sign in",
        icon=":material/login:",
    )
    st.stop()

current_user = get_current_user()

st.subheader("Identity")

if current_user is None:
    st.info("Your account is signed in, but your CODHEM profile is not complete yet.")
    st.page_link(
        "pages/account/complete_registration.py",
        label="Complete registration",
        icon=":material/person_add:",
    )
    st.stop()

profile_rows = [
    {
        "Full Name": current_user.name or get_current_identity_name(),
        "Email": get_current_identity_email(),
        "Role": current_user.role,
        "Organization": current_user.organization,
        "Country": current_user.country,
        "Position": current_user.position,
    }
]

edited_rows = st.data_editor(
    profile_rows,
    width="stretch",
    hide_index=True,
    num_rows="fixed",
    disabled=["Email", "Role"],
    column_config={
        "Full Name": st.column_config.TextColumn(required=True),
        "Email": st.column_config.TextColumn(),
        "Role": st.column_config.TextColumn(),
        "Organization": st.column_config.TextColumn(required=True),
        "Country": st.column_config.TextColumn(required=True),
        "Position": st.column_config.SelectboxColumn(
            options=[
                "Student",
                "Researcher",
                "Professor",
                "Private Sector Employee",
                "Other",
            ],
            required=True,
        ),
    },
    key="profile-editor",
)

if st.button("Save Profile", width="stretch", key="save-profile"):
    edited_row = edited_rows[0]
    success, message = update_current_user_profile(
        edited_row["Full Name"],
        edited_row["Organization"],
        edited_row["Country"],
        edited_row["Position"],
    )
    if success:
        st.success(message)
        st.rerun()
    else:
        st.error(message)
