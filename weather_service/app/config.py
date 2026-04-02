from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str
    redis_port: int
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_management_port: int
    app_port: int
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str

    class Config:
        env_file = ".env"


settings = Settings()
