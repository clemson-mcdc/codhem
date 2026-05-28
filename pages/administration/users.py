import streamlit as st

from codhem.services.auth_service import list_users, require_role, update_user

require_role("Admin")

users = [
    {
        "Original Email": user.email,
        "Name": user.name,
        "Email": user.email,
        "Role": user.role,
        "Organization": user.organization,
        "Country": user.country,
        "Position": user.position,
        "Verified": user.verified,
    }
    for user in list_users()
]

st.title("Users")
st.caption("Manage application users and access roles.")

edited_users = st.data_editor(
    users,
    width="stretch",
    hide_index=True,
    num_rows="fixed",
    column_order=[
        "Name",
        "Email",
        "Role",
        "Organization",
        "Country",
        "Position",
        "Verified",
    ],
    column_config={
        "Original Email": None,
        "Verified": st.column_config.CheckboxColumn(),
    },
    key="users-editor",
)

if st.button("Save Users", width="stretch", key="save-users"):
    for edited_user in edited_users:
        success, message = update_user(
            edited_user["Original Email"],
            edited_user["Name"],
            edited_user["Email"],
            edited_user["Role"],
            edited_user["Organization"],
            edited_user["Country"],
            edited_user["Position"],
            edited_user["Verified"],
        )
        if not success:
            st.error(message)
            st.stop()

    st.success("User records updated.")
    st.rerun()
