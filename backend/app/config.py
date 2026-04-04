from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/hr_digest"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    anthropic_api_key: str = ""
    resend_api_key: str = ""
    frontend_url: str = "http://localhost:3000"
    email_from: str = "HR Digest <digest@example.com>"

    class Config:
        env_file = ".env"


settings = Settings()
