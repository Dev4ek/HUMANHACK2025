from pydantic import AnyHttpUrl, ConfigDict, BaseModel
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    
    SQLALCHEMY_DATABASE_URL: str
    SQLALCHEMY_DATABASE_SYNC_URL: str

    WORKERS: int = 1
    HOST: str = "0.0.0.0"
    
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")   

settings = Settings()
