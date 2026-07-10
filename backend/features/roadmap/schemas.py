from pydantic import BaseModel


class EmployeeProfile(BaseModel):
    name: str
    role: str
    years_experience: int
    current_skills: list[str]
    career_goal: str


class ConceptModule(BaseModel):
    name: str
    topics: list[str]
    concepts: list[str]
    milestone: str


class MonthPlan(BaseModel):
    month: int
    theme: str
    modules: list[ConceptModule]


class Roadmap(BaseModel):
    employee: EmployeeProfile
    goal: str
    roadmap: list[MonthPlan]


class RoadmapRequest(BaseModel):
    profile: EmployeeProfile


class RoadmapResponse(BaseModel):
    roadmap: Roadmap
