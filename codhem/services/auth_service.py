import streamlit as st

from codhem.db.client import DatabaseClient
from codhem.models.auth import User


def _get_users_collection():
    client = DatabaseClient()
    return client.get_collection("users")


def _normalize_email(email: str):
    return email.strip().lower()


def _to_user(document):
    return User(
        name=document["name"],
        email=document["email"],
        role=document["role"],
        organization=document["organization"],
        country=document.get("country", ""),
        position=document.get("position", ""),
        verified=bool(document.get("verified", False)),
    )


def _current_user_claim(claim_name: str, default: str = ""):
    return str(st.user.get(claim_name, default)).strip()


def list_users():
    collection = _get_users_collection()
    documents = collection.find({}, {"_id": 0}).sort("name", 1)
    return [_to_user(document) for document in documents]


def is_authenticated():
    return bool(getattr(st.user, "is_logged_in", False))


def get_current_identity_email():
    if not is_authenticated():
        return ""
    return _normalize_email(_current_user_claim("email"))


def get_current_identity_name():
    if not is_authenticated():
        return ""
    name = _current_user_claim("name")
    if name:
        return name
    return get_current_identity_email()


def get_current_user():
    email = get_current_identity_email()
    if not email:
        return None

    document = _get_users_collection().find_one({"email": email}, {"_id": 0})
    if document is None:
        return None
    return _to_user(document)


def is_registered_user():
    return get_current_user() is not None


def get_current_user_role():
    user = get_current_user()
    if user is None:
        return ""
    return user.role


def is_verified_user():
    user = get_current_user()
    if user is None:
        return False
    return user.verified


def require_auth():
    if is_authenticated():
        return
    st.switch_page("pages/account/sign_in.py")
    st.stop()


def require_registered_user():
    require_auth()
    if is_verified_user():
        return
    st.switch_page("pages/account/complete_registration.py")
    st.stop()


def require_role(role: str):
    require_registered_user()
    if get_current_user_role() == role:
        return
    st.switch_page("pages/account/complete_registration.py")
    st.stop()


def register_current_user(
    name: str,
    organization: str,
    country: str,
    position: str,
    default_role: str = "Viewer",
):
    email = get_current_identity_email()
    if not email:
        return False, "You must be signed in before completing registration."

    normalized_name = name.strip()
    normalized_organization = organization.strip()
    normalized_country = country.strip()
    normalized_position = position.strip()
    if not normalized_name:
        return False, "Full name is required."
    if not normalized_organization:
        return False, "Organization is required."
    if not normalized_country:
        return False, "Country is required."
    if not normalized_position:
        return False, "Position is required."

    collection = _get_users_collection()
    if collection.find_one({"email": email}) is not None:
        return False, "This account is already registered."

    collection.insert_one(
        {
            "name": normalized_name,
            "email": email,
            "role": default_role,
            "organization": normalized_organization,
            "country": normalized_country,
            "position": normalized_position,
            "verified": False,
        }
    )
    return True, "Your CODHEM profile has been created. An administrator must verify your account before you can access the site."


def update_current_user_profile(
    name: str,
    organization: str,
    country: str,
    position: str,
):
    email = get_current_identity_email()
    if not email:
        return False, "You must be signed in before updating your profile."

    normalized_name = name.strip()
    normalized_organization = organization.strip()
    normalized_country = country.strip()
    normalized_position = position.strip()
    if not normalized_name:
        return False, "Full name is required."
    if not normalized_organization:
        return False, "Organization is required."
    if not normalized_country:
        return False, "Country is required."
    if not normalized_position:
        return False, "Position is required."

    collection = _get_users_collection()
    update_result = collection.update_one(
        {"email": email},
        {
            "$set": {
                "name": normalized_name,
                "organization": normalized_organization,
                "country": normalized_country,
                "position": normalized_position,
            }
        },
    )
    if update_result.matched_count == 0:
        return False, "This account does not have a CODHEM profile yet."

    return True, "Your CODHEM profile has been updated."


def update_user(
    original_email: str,
    name: str,
    email: str,
    role: str,
    organization: str,
    country: str,
    position: str,
    verified: bool,
):
    normalized_original_email = _normalize_email(original_email)
    normalized_email = _normalize_email(email)
    normalized_name = name.strip()
    normalized_role = role.strip()
    normalized_organization = organization.strip()
    normalized_country = country.strip()
    normalized_position = position.strip()

    if not normalized_original_email:
        return False, "Original email is required."
    if not normalized_name:
        return False, "Full name is required."
    if not normalized_email:
        return False, "Email is required."
    if not normalized_role:
        return False, "Role is required."
    if not normalized_organization:
        return False, "Organization is required."
    if not normalized_country:
        return False, "Country is required."
    if not normalized_position:
        return False, "Position is required."

    collection = _get_users_collection()
    existing_user = collection.find_one(
        {"email": normalized_email},
        {"_id": 0, "email": 1},
    )
    if existing_user is not None and normalized_email != normalized_original_email:
        return False, f"{normalized_email} is already registered."

    update_result = collection.update_one(
        {"email": normalized_original_email},
        {
            "$set": {
                "name": normalized_name,
                "email": normalized_email,
                "role": normalized_role,
                "organization": normalized_organization,
                "country": normalized_country,
                "position": normalized_position,
                "verified": bool(verified),
            }
        },
    )
    if update_result.matched_count == 0:
        return False, f"{normalized_original_email} was not found."

    return True, f"Updated {normalized_email}."


def sign_out():
    st.logout()
