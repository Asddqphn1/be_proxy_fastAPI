from pydantic_settings import BaseSettings, SettingsConfigDict

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


    model_config = _base_config


security_settings = SecuritySettings()


