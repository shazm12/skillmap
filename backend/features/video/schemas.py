from pydantic import BaseModel


class VideoRequest(BaseModel):
    concept_name: str
    concept_description: str
    context: str = ""  # optional roadmap context for better script


class Storyboard(BaseModel):
    scenes: list[dict]  # each scene: {title, bullets, duration_seconds}
    total_duration: int = 60


class VideoResponse(BaseModel):
    video_path: str
    concept_name: str
    duration_seconds: int
