from pydantic_settings import BaseSettings, SettingsConfigDict


#settings class for database connection and other settings
class Setting(BaseSettings):

    model_config = SettingsConfigDict(
    env_file='.env' ,
    env_file_encoding="utf-8", 
    extra='ignore')

    DATABASE_URL : str

settings = Setting()