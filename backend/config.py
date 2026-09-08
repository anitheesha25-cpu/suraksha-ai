from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./suraksha.db"
    cors_origins: str = "http://localhost:5173"
    open_meteo_base: str = "https://api.open-meteo.com/v1/forecast"
    usgs_feed: str = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
