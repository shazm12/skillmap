from app.pipelines.roadmap.schemas import EmployeeProfile


class ProfileAnalystAgent:
    """
    Parses the user's free-text prompt and extracts structured profile info:
    role, years of experience, current skills, and career goal.
    """

    async def run(self, prompt: str) -> EmployeeProfile:
        raise NotImplementedError


class GoalStrategistAgent:
    """
    Decomposes the career goal into 6 monthly sub-goals
    tailored to the extracted profile.
    """

    async def run(self, profile: EmployeeProfile) -> dict:
        raise NotImplementedError


class CurriculumDesignerAgent:
    """
    Maps each monthly sub-goal to concrete modules,
    topics, and concepts.
    """

    async def run(self, sub_goals: dict, profile: EmployeeProfile) -> dict:
        raise NotImplementedError


class PersonalizerAgent:
    """
    Adjusts depth, pace, and difficulty of the curriculum based on experience level,
    then renders the final roadmap as a structured Markdown string.

    Output format:
    # 6-Month Roadmap: <goal>
    ## Month 1: <theme>
    ### <Module Name>
    **Topics:** ...
    **Key Concepts:** ...
    **Milestone:** ...
    """

    async def run(self, curriculum: dict, profile: EmployeeProfile) -> str:
        raise NotImplementedError
