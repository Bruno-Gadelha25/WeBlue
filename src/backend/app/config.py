from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # =========================
    # BANCO DE DADOS
    # =========================

    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "weblue"

    # =========================
    # JWT
    # =========================

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # =========================
    # ARQUIVO .ENV
    # =========================

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()