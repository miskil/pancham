from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost/pancham"
    jwt_secret: str = "changeme"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    admin_username: str = "admin"
    admin_password: str = "changeme"
    donor_token: str = ""
    storage_bucket: str = "pancham-media"
    storage_url: str = ""
    bhau_api_url: str = "https://bhau.railway.app"
    bhau_enabled: bool = False
    enable_reset_tables_endpoint: bool = False

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if isinstance(value, str):
            if value.startswith("postgres://"):
                return value.replace("postgres://", "postgresql+asyncpg://", 1)
            if value.startswith("postgresql://") and "+asyncpg" not in value:
                return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
