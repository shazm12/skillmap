from pydantic_settings import BaseSettings


class DevSettings(BaseSettings):
    APP_NAME: str = "Career Roadmap Platform"
    APP_VERSION: str = "0.1.0"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-20b"

    LIVEKIT_URL: str = ""
    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""

    DEEPGRAM_API_KEY: str = ""
    CARTESIA_API_KEY: str = ""

    CORS_ORIGINS: list[str] = [""]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


dev_settings = DevSettings()
