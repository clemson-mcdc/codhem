from dataclasses import dataclass
from pathlib import Path
import tomllib

from codhem.config.constants import DEFAULT_DATASET_LIMIT


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    name: str
    username: str
    password: str


@dataclass(frozen=True)
class ModelApiSettings:
    host: str
    port: int
    base_path: str


@dataclass(frozen=True)
class LlmSettings:
    api_key: str
    base_url: str
    model: str
    system_prompt: str


@dataclass(frozen=True)
class Settings:
    app_name: str
    dataset_limit: int
    database: DatabaseSettings
    model_api: ModelApiSettings
    llm: LlmSettings


def get_settings():
    config_path = Path(__file__).resolve().parents[2] / "config.toml"
    with config_path.open("rb") as config_file:
        config = tomllib.load(config_file)

    database_config = config["database"]
    model_api_config = config.get("model_api", {})
    llm_config = config.get("llm", {})

    return Settings(
        app_name=config.get("app", {}).get("name", "codhem"),
        dataset_limit=config.get("app", {}).get("dataset_limit", DEFAULT_DATASET_LIMIT),
        database=DatabaseSettings(
            host=database_config["host"],
            port=database_config["port"],
            name=database_config["name"],
            username=database_config.get("username", ""),
            password=database_config.get("password", ""),
        ),
        model_api=ModelApiSettings(
            host=model_api_config.get("host", "127.0.0.1"),
            port=model_api_config.get("port", 8000),
            base_path=model_api_config.get("base_path", "/api/ml-models"),
        ),
        llm=LlmSettings(
            api_key=llm_config.get("api_key", ""),
            base_url=llm_config.get("base_url", "https://llm.rcd.clemson.edu/v1"),
            model=llm_config.get("model", "gptoss-120b"),
            system_prompt=llm_config.get(
                "system_prompt",
                "You are a helpful assistant.",
            ),
        ),
    )
