from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.pipelines.roadmap.agents import (
    CurriculumDesignerAgent,
    GoalStrategistAgent,
    PersonalizerAgent,
    ProfileAnalystAgent,
)
from app.pipelines.roadmap.schemas import EmployeeProfile


class RoadmapState(TypedDict):
    profile: EmployeeProfile
    analysis: dict
    sub_goals: dict
    curriculum: dict
    final_roadmap: dict


def build_roadmap_graph() -> StateGraph:
    analyst = ProfileAnalystAgent()
    strategist = GoalStrategistAgent()
    designer = CurriculumDesignerAgent()
    personalizer = PersonalizerAgent()

    graph = StateGraph(RoadmapState)

    graph.add_node("profile_analyst", lambda s: {"analysis": analyst.run(s["profile"])})
    graph.add_node("goal_strategist", lambda s: {"sub_goals": strategist.run(s["profile"], s["analysis"])})
    graph.add_node("curriculum_designer", lambda s: {"curriculum": designer.run(s["sub_goals"], s["profile"])})
    graph.add_node("personalizer", lambda s: {"final_roadmap": personalizer.run(s["curriculum"], s["profile"])})

    graph.set_entry_point("profile_analyst")
    graph.add_edge("profile_analyst", "goal_strategist")
    graph.add_edge("goal_strategist", "curriculum_designer")
    graph.add_edge("curriculum_designer", "personalizer")
    graph.add_edge("personalizer", END)

    return graph.compile()
