import json
from urllib import error, request

import streamlit as st

from codhem.config.settings import get_settings
from codhem.services.auth_service import require_registered_user

MODEL_TITLE = "RHEA-DOS-E Predictor"
MODEL_SUMMARY = (
    "Predicts the electronic density of states at the Fermi level and Young's "
    "modulus for refractory high-entropy alloys."
)
MODEL_DESCRIPTION = (
    "RHEA-DOS-E Predictor estimates the electronic density of states at the "
    "Fermi level, N(Ef), and Young's modulus of refractory high-entropy alloys "
    "using a machine learning model trained on density functional theory data.\n\n"
    "Provide an alloy composition in atomic percent that sums to 100, such as "
    "Cr20Mo30V10Hf40. The model derives composition-based descriptors and "
    "returns electronic structure and elastic-property predictions without "
    "requiring a fresh DFT calculation."
)
COMPOSITION_HINT = (
    "Provide alloy composition in atomic percent that sums to 100 "
    "(for example, Cr20Mo30V10Hf40). Values are normalized by the backend "
    "when needed."
)


def _get_model_api_url():
    model_api_settings = get_settings().model_api
    return (
        f"http://{model_api_settings.host}:{model_api_settings.port}"
        f"{model_api_settings.base_path.rstrip('/')}/rhea-mpnn/predict"
    )


def _parse_error_message(response_body: bytes, fallback_message: str):
    if not response_body:
        return fallback_message

    try:
        payload = json.loads(response_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return fallback_message

    detail = payload.get("detail")
    if isinstance(detail, str) and detail.strip():
        return detail
    return fallback_message


def _run_prediction(composition: str):
    normalized_composition = composition.strip()
    if not normalized_composition:
        raise RuntimeError("Composition is required.")

    http_request = request.Request(
        _get_model_api_url(),
        data=json.dumps({"composition": normalized_composition}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        error_message = _parse_error_message(
            exc.read(),
            f"Model API request failed with status {exc.code}.",
        )
        raise RuntimeError(error_message) from exc
    except error.URLError as exc:
        raise RuntimeError(
            "Model API is not reachable. Confirm the local model server is running."
        ) from exc


require_registered_user()

st.title(MODEL_TITLE)
st.caption(MODEL_SUMMARY)
st.write(MODEL_DESCRIPTION)

st.page_link(
    "pages/ml_models/overview.py",
    label="Back to model list",
    icon=":material/arrow_back:",
)

st.subheader("Inputs")

with st.form("rhea-mpnn-input-form"):
    composition = st.text_input("Composition", help=COMPOSITION_HINT)
    submitted = st.form_submit_button("Run model", width="stretch")

st.subheader("Outputs")
st.caption(
    "DOS at Fermi Level, N(Ef): Predicted electronic density of states at the "
    "Fermi level in states/eV-atom."
)
st.caption(
    "Young's Modulus (GPa): Predicted elastic modulus under the VRH approximation."
)

if submitted:
    try:
        prediction = _run_prediction(composition)
    except RuntimeError as exc:
        st.error(str(exc))
    else:
        left_col, right_col = st.columns(2)
        left_col.metric(
            "DOS at Fermi Level, N(Ef)",
            f"{float(prediction['dos_at_fermi']):.4f}",
        )
        right_col.metric(
            "Young's Modulus (GPa)",
            f"{float(prediction['youngs_modulus_gpa']):.4f}",
        )
        st.caption(f"Composition: {prediction['composition']}")
