from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Career Roadmap Platform"
    APP_VERSION: str = "0.1.0"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    VIDEO_OUTPUT_DIR: str = "output/videos"
    AUDIO_OUTPUT_DIR: str = "output/audio"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
