import os
import secrets
from pydantic_settings import BaseSettings
from pydantic import model_validator


def generate_secret_key() -> str:
    """Generate a secure random secret key"""
    return secrets.token_urlsafe(32)


class Settings(BaseSettings):
    bot_token: str = ""
    bot_username: str = "TaskAppBot"
    admin_api_key: str = "admin_secret_key"
    database_url: str = "sqlite:///./task_app.db"
    admin_user_ids: str = ""
    web_app_url: str = "http://localhost:8000"
    port: int = 8000
    admin_username: str = "admin"
    admin_password: str = "admin123"
    secret_key: str = ""
    use_secure_cookies: bool = False  # Set to True in production with HTTPS
    
    @model_validator(mode='after')
    def generate_secret_if_needed(self):
        """Generate a secure secret key if not provided"""
        if not self.secret_key:
            self.secret_key = generate_secret_key()
        return self
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def admin_ids(self) -> list:
        if self.admin_user_ids:
            return [int(uid.strip()) for uid in self.admin_user_ids.split(",") if uid.strip()]
        return []


settings = Settings()
