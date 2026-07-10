from app.pipelines.roadmap.schemas import EmployeeProfile


class ProfileAnalystAgent:
    """
    Analyzes the employee profile to identify skill gaps,
    seniority level, and recommended learning pace.
    """

    async def run(self, profile: EmployeeProfile) -> dict:
        raise NotImplementedError


class GoalStrategistAgent:
    """
    Decomposes the career goal into 6 monthly sub-goals
    based on the analyst's output.
    """

    async def run(self, profile: EmployeeProfile, analysis: dict) -> dict:
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
    Adjusts depth, pace, and difficulty of the curriculum
    based on the employee's experience level.
    """

    async def run(self, curriculum: dict, profile: EmployeeProfile) -> dict:
        raise NotImplementedError
