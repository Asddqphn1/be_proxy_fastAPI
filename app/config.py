from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import urlsplit


def _normalize_origin(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return url.rstrip("/")

_base_config = SettingsConfigDict(
    env_file=".env",
    env_ignore_empty=True,
    extra="ignore",

)

class SecuritySettings(BaseSettings):

    REDIS_HOST: str = "localhost" 
    REDIS_PORT: int = 6379   
    KEYCLOAK_ISSUER: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_REDIRECT_URI: str
    FRONTEND_URL: str
    API_GATEWAY_URL: str
    FRONTEND_ORIGINS: str = ""
    SESSION_TTL_SECONDS: int = 1800
    OAUTH_STATE_TTL_SECONDS: int = 300
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"


    model_config = _base_config

    @property
    def cors_origins(self) -> list[str]:
        if self.FRONTEND_ORIGINS:
            return [_normalize_origin(origin.strip()) for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]
        return [_normalize_origin(self.FRONTEND_URL)]


security_settings = SecuritySettings()


