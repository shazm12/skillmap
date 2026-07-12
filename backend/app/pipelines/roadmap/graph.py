from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.pipelines.roadmap.agents import (
    CurriculumDesignerAgent,
    GoalStrategistAgent,
    PersonalizerAgent,
    ProfileAnalystAgent,
)
from app.pipelines.roadmap.schemas import Curriculum, EmployeeProfile, SubGoals


class RoadmapState(TypedDict):
    prompt: str
    should_continue: bool
    rejection_reason: str
    profile: EmployeeProfile
    sub_goals: SubGoals
    curriculum: Curriculum
    final_roadmap: str


_analyst = ProfileAnalystAgent()
_strategist = GoalStrategistAgent()
_designer = CurriculumDesignerAgent()
_personalizer_agent = PersonalizerAgent()


async def _profile_analyst(state: RoadmapState) -> dict:
    result = await _analyst.run(state["prompt"])
    profile = EmployeeProfile(
        role=result.role,
        years_experience=result.years_experience,
        current_skills=result.current_skills,
        career_goal=result.career_goal,
    )
    return {
        "should_continue": result.should_continue,
        "rejection_reason": result.rejection_reason,
        "profile": profile,
    }


def _reject(state: RoadmapState) -> dict:
    return {
        "final_roadmap": (
            "# Cannot Process Request\n\n"
            f"{state['rejection_reason']}\n\n"
            "I can only help with career roadmaps for **Software Engineers**, "
            "**ML/AI Engineers**, **Product Managers**, and **Tech Leads**."
        )
    }


def _route(state: RoadmapState) -> str:
    return "goal_strategist" if state["should_continue"] else "reject"


async def _goal_strategist(state: RoadmapState) -> dict:
    return {"sub_goals": await _strategist.run(state["profile"])}


async def _curriculum_designer(state: RoadmapState) -> dict:
    return {"curriculum": await _designer.run(state["sub_goals"], state["profile"])}


async def _personalizer(state: RoadmapState) -> dict:
    return {"final_roadmap": await _personalizer_agent.run(state["curriculum"], state["profile"])}


def build_roadmap_graph() -> StateGraph:
    graph = StateGraph(RoadmapState)

    graph.add_node("profile_analyst", _profile_analyst)
    graph.add_node("goal_strategist", _goal_strategist)
    graph.add_node("curriculum_designer", _curriculum_designer)
    graph.add_node("personalizer", _personalizer)
    graph.add_node("reject", _reject)

    graph.set_entry_point("profile_analyst")
    graph.add_conditional_edges("profile_analyst", _route)
    graph.add_edge("goal_strategist", "curriculum_designer")
    graph.add_edge("curriculum_designer", "personalizer")
    graph.add_edge("personalizer", END)
    graph.add_edge("reject", END)

    return graph.compile()
