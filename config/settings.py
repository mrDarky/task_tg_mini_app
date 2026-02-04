import os
import secrets
import logging
from pydantic_settings import BaseSettings
from pydantic import model_validator


logger = logging.getLogger(__name__)


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
            logger.warning(
                "SECRET_KEY not set in environment. Auto-generated a temporary key. "
                "All sessions will be invalidated on application restart. "
                "For production, set SECRET_KEY in .env file."
            )
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
