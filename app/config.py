import os
import hvac
from functools import lru_cache


def _get_vault_client() -> hvac.Client:
    """Authenticate to Vault using AppRole and return an authenticated client."""
    vault_addr = os.environ.get("VAULT_ADDR", "http://localhost:8200")
    role_id = os.environ.get("VAULT_ROLE_ID")
    secret_id = os.environ.get("VAULT_SECRET_ID")

    if not role_id or not secret_id:
        raise EnvironmentError(
            "VAULT_ROLE_ID and VAULT_SECRET_ID must be set. "
            "Never hardcode secrets — fetch them from Vault."
        )

    client = hvac.Client(url=vault_addr)
    client.auth.approle.login(role_id=role_id, secret_id=secret_id)

    if not client.is_authenticated():
        raise RuntimeError("Vault authentication failed. Check your AppRole credentials.")

    return client


@lru_cache(maxsize=1)
def _load_secrets() -> dict:
    """Load all app secrets from Vault once and cache them in memory."""
    client = _get_vault_client()

    db_secret = client.secrets.kv.v2.read_secret_version(
        path="secureship/db", mount_point="secret"
    )
    app_secret = client.secrets.kv.v2.read_secret_version(
        path="secureship/app", mount_point="secret"
    )

    return {
        "db": db_secret["data"]["data"],
        "app": app_secret["data"]["data"],
    }


class Settings:
    """Application settings — all values come from Vault, never from source code."""

    def __init__(self):
        secrets = _load_secrets()
        self.DATABASE_URL: str = secrets["db"]["url"]
        self.SECRET_KEY: str = secrets["app"]["secret_key"]
        self.JWT_ALGORITHM: str = secrets["app"]["jwt_algorithm"]
        self.JWT_EXPIRE_MINUTES: int = int(secrets["app"]["jwt_expire_minutes"])

    def __repr__(self):
        return "Settings(secrets=<redacted>)"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
