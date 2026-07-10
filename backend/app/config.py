from pydantic_settings import BaseSettings


class DevSettings(BaseSettings):
    APP_NAME: str = "Career Roadmap Platform"
    APP_VERSION: str = "0.1.0"

    GROQ_API_KEY: str = ""

    # Qwen3 32B — quantized, reasoning-capable, low latency on Groq
    # Groq model ID: https://console.groq.com/docs/models
    GROQ_MODEL: str = "qwen/qwen3-32b"

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    VIDEO_OUTPUT_DIR: str = "output/videos"
    AUDIO_OUTPUT_DIR: str = "output/audio"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


dev_settings = DevSettings()
