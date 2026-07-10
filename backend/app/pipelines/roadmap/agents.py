from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.config import dev_settings as settings
from app.pipelines.roadmap.schemas import (
    Curriculum,
    EmployeeProfile,
    SubGoals,
)


class RoadmapAgentError(Exception):
    """Raised when an agent fails to produce a valid response."""
    pass


def _llm() -> ChatGroq:
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
    )


def _structured_llm(schema):
    # json_mode is more reliable than tool calling for Qwen3 on Groq
    return _llm().with_structured_output(schema, method="json_mode")


class ProfileAnalystAgent:
    _prompt = """\
You are a career profile extractor. Respond with valid JSON only.
From the user's message, extract their current role, years of experience, \
current skills, and career goal. Infer missing details reasonably.

Return JSON with exactly these snake_case field names:
{"role": str, "years_experience": int, "current_skills": [str], "career_goal": str}"""

    async def run(self, prompt: str) -> EmployeeProfile:
        try:
            llm = _structured_llm(EmployeeProfile)
            return await llm.ainvoke([
                SystemMessage(content=self._prompt),
                HumanMessage(content=prompt),
            ])
        except Exception as e:
            raise RoadmapAgentError(f"ProfileAnalyst failed: {e}") from e


class GoalStrategistAgent:
    _prompt = """\
You are a career growth strategist. Respond with valid JSON only.
Create a 6-month plan with monthly themes for the given employee profile.

Return JSON with exactly these snake_case field names:
{"career_path": str, "sub_goals": [{"month": int, "theme": str, "focus": str}]}


Supported career paths and their progression arc:
- Senior Software Engineer: system design → scalability → code quality → \
mentorship → cross-team influence → technical vision
- ML/AI Engineer: math & stats → ML fundamentals → deep learning → \
MLOps → LLM & GenAI → production AI systems
- Product Manager: product thinking → user research → roadmapping → \
stakeholder management → metrics & growth → strategy
- Tech Lead: technical leadership → architecture decisions → team processes \
→ delivery & execution → people skills → org influence

Pacing rules:
- <2 yrs exp: fundamentals first, build confidence
- 2–5 yrs exp: deepen expertise, add breadth
- 5+ yrs exp: leadership, specialization, influence

Each month must have one clear theme and a one-sentence focus. \
Month N+1 must build on month N."""

    async def run(self, profile: EmployeeProfile) -> SubGoals:
        try:
            llm = _structured_llm(SubGoals)
            content = (
                f"Role: {profile.role}\n"
                f"Experience: {profile.years_experience} years\n"
                f"Skills: {', '.join(profile.current_skills)}\n"
                f"Goal: {profile.career_goal}"
            )
            return await llm.ainvoke([
                SystemMessage(content=self._prompt),
                HumanMessage(content=content),
            ])
        except Exception as e:
            raise RoadmapAgentError(f"GoalStrategist failed: {e}") from e


class CurriculumDesignerAgent:
    _prompt = """\
You are a curriculum designer for tech career development. Respond with valid JSON only.
Design detailed learning modules for each month based on the sub-goals.

Return JSON with exactly these snake_case field names:
{"months": [{"month": int, "theme": str, "modules": [{"name": str, "topics": [str], "concepts": [str], "milestone": str}]}]}


Knowledge map by career path (use as reference, not exhaustive):
- Senior Software Engineer: distributed systems, SQL/NoSQL databases, REST & \
GraphQL API design, testing strategies, CI/CD, system design patterns, \
code review, performance profiling, mentoring techniques
- ML/AI Engineer: linear algebra & probability, numpy/pandas/sklearn, \
neural networks & backprop, CNNs/RNNs/Transformers, fine-tuning LLMs, \
MLOps (MLflow, DVC), vector databases, LangChain, RAG, model evaluation
- Product Manager: product discovery, user interviews & personas, writing PRDs, \
prioritization (RICE, MoSCoW, Kano), OKRs & KPIs, A/B testing, \
roadmapping, go-to-market strategy, stakeholder communication
- Tech Lead: technical strategy, Architecture Decision Records (ADRs), \
team topologies, agile/scrum facilitation, performance reviews, \
incident management, DORA metrics, engineering culture, hiring

Rules:
- 2–3 modules per month
- 3–5 topics per module, 3–5 key concepts per module
- One concrete milestone per module (a project, deliverable, or assessment)
- Junior profiles: more foundational modules; senior profiles: \
more advanced, leadership-oriented modules"""

    async def run(self, sub_goals: SubGoals, profile: EmployeeProfile) -> Curriculum:
        try:
            llm = _structured_llm(Curriculum)
            monthly_plan = "\n".join(
                f"Month {g.month}: {g.theme} — {g.focus}"
                for g in sub_goals.sub_goals
            )
            content = (
                f"Profile: {profile.role}, {profile.years_experience} yrs exp, "
                f"goal: {profile.career_goal}\n"
                f"Career path: {sub_goals.career_path}\n\n"
                f"Monthly themes:\n{monthly_plan}"
            )
            return await llm.ainvoke([
                SystemMessage(content=self._prompt),
                HumanMessage(content=content),
            ])
        except Exception as e:
            raise RoadmapAgentError(f"CurriculumDesigner failed: {e}") from e


class PersonalizerAgent:
    _prompt = """\
You are a learning roadmap formatter.
Render the curriculum as a clean, scannable Markdown document. \
Return ONLY the markdown — no preamble, no explanation.

Required format:
# 6-Month Roadmap: {career_goal}
> {role} · {years_experience} years experience

---

## Month N: {theme}

### {Module Name}
**Topics:** topic1, topic2, topic3
**Key Concepts:** concept1, concept2, concept3
**Milestone:** one concrete thing to build or complete

Personalization rules:
- <2 yrs exp: add beginner-friendly framing; keep language approachable
- 5+ yrs exp: emphasize architecture, leadership, and advanced depth
- No long paragraphs — short, scannable lines only"""

    async def run(self, curriculum: Curriculum, profile: EmployeeProfile) -> str:
        try:
            llm = _llm()
            content = (
                f"Profile: {profile.role}, {profile.years_experience} yrs, "
                f"goal: {profile.career_goal}\n\n"
                f"Curriculum:\n{curriculum.model_dump_json(indent=2)}"
            )
            response = await llm.ainvoke([
                SystemMessage(content=self._prompt),
                HumanMessage(content=content),
            ])
            return response.content
        except Exception as e:
            raise RoadmapAgentError(f"Personalizer failed: {e}") from e
