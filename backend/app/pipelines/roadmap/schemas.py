from pydantic import BaseModel, Field


class RoadmapRequest(BaseModel):
    prompt: str


class ProfileAnalystOutput(BaseModel):
    should_continue: bool = Field(
        description="True if the prompt is about career development or learning goals. False if off-topic."
    )
    rejection_reason: str = Field(
        description="If should_continue is False, a brief explanation why. Empty string if should_continue is True."
    )
    role: str = Field(description="Current job title or role")
    years_experience: int = Field(description="Years of professional experience, infer if not stated")
    current_skills: list[str] = Field(description="Current technical or domain skills")
    career_goal: str = Field(description="Target role the person wants to reach")


class EmployeeProfile(BaseModel):
    role: str = Field(description="Current job title or role")
    years_experience: int = Field(description="Years of professional experience, infer if not stated")
    current_skills: list[str] = Field(description="Current technical or domain skills")
    career_goal: str = Field(description="Target role the person wants to reach")


class MonthlySubGoal(BaseModel):
    month: int = Field(description="Month number starting from 1", ge=1)
    theme: str = Field(description="Short theme title, e.g. 'ML Fundamentals'")
    focus: str = Field(description="One sentence describing the key focus for this month")


class SubGoals(BaseModel):
    career_path: str = Field(description="One of: Senior Software Engineer, ML/AI Engineer, Product Manager, Tech Lead")
    sub_goals: list[MonthlySubGoal] = Field(
        description="3 to 9 monthly sub-goals based on goal complexity and experience level",
        min_length=3,
        max_length=9,
    )


class TopicModule(BaseModel):
    name: str = Field(description="Module name")
    topics: list[str] = Field(description="3 to 5 topics to study")
    concepts: list[str] = Field(description="3 to 5 key concepts to understand")
    milestone: str = Field(description="One concrete deliverable or achievement to complete")


class MonthCurriculum(BaseModel):
    month: int = Field(description="Month number starting from 1", ge=1)
    theme: str = Field(description="Month theme, matching the sub-goal theme")
    modules: list[TopicModule] = Field(
        description="2 to 3 learning modules for this month",
        min_length=2,
        max_length=3,
    )


class Curriculum(BaseModel):
    months: list[MonthCurriculum] = Field(
        description="3 to 9 months of curriculum matching the sub-goals, one entry per month",
        min_length=3,
        max_length=9,
    )

