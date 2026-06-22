import json
from urllib import error, request

from codhem.config.settings import get_settings


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


def run_rhea_mpnn_prediction(composition: str):
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
