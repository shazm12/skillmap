from pydantic import BaseModel


class RoadmapRequest(BaseModel):
    prompt: str


class EmployeeProfile(BaseModel):
    role: str
    years_experience: int
    current_skills: list[str]
    career_goal: str


class RoadmapResponse(BaseModel):
    markdown: str  # full roadmap as markdown, ready for frontend rendering
