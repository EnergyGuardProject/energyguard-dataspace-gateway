from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="DATASPACE_", extra="ignore")

    enpower_base_url: str = "https://enpower.eurodyn.com"
    connector_base_url: str = "https://true-connector-1-server-localapi.eurodyn.com"
    request_timeout: float = 30.0
    cors_allowed_origins: str = "*"

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_allowed_origins.split(",")]
        return [origin for origin in origins if origin]


settings = Settings()
