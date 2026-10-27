from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    redis_url: str
    rabbitmq_url: str
    mock_gateway_url: str = "http://localhost:8003/mock-gateway"
    service_name: str = "payment-service"
    log_level: str = "INFO"


settings = Settings()