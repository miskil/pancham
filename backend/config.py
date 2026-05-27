from pydantic_settings import BaseSettings


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

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
