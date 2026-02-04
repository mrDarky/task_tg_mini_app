import os
from pydantic_settings import BaseSettings


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
    secret_key: str = "your-secret-key-change-this-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def admin_ids(self) -> list:
        if self.admin_user_ids:
            return [int(uid.strip()) for uid in self.admin_user_ids.split(",") if uid.strip()]
        return []


settings = Settings()
