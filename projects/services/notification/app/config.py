from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    rabbitmq_url: str
    service_name: str = "notification-service"
    log_level: str = "INFO"

    smtp_host: str
    smtp_port: int = 465
    smtp_user: str
    smtp_password: str
    smtp_from: str
    smtp_use_tls: bool = False
    smtp_start_tls: bool = True


settings = Settings()