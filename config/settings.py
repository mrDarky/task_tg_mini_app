import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str = ""
    admin_api_key: str = "admin_secret_key"
    database_url: str = "sqlite:///./task_app.db"
    admin_user_ids: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def admin_ids(self) -> list:
        if self.admin_user_ids:
            return [int(uid.strip()) for uid in self.admin_user_ids.split(",") if uid.strip()]
        return []


settings = Settings()
