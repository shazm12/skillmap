from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.config import dev_settings as settings
from app.pipelines.roadmap.schemas import (
    Curriculum,
    EmployeeProfile,
    ProfileAnalystOutput,
    SubGoals,
)


class RoadmapAgentError(Exception):
    """Raised when an agent fails to produce a valid response."""
    pass


def _llm() -> ChatGroq:
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0,
    )


def _structured_llm(schema):
    # temperature=0 reduces schema deviation; with_retry absorbs remaining transient failures
    llm = ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0,
    )
    return llm.with_structured_output(schema, method="json_mode").with_retry(
        stop_after_attempt=3
    )


class ProfileAnalystAgent:
    _prompt = """\
You are a career profile extractor and input validator. Respond with valid JSON only.

First, decide if the user's message is genuinely about career development or \
learning goals (role transitions, skill building, career growth). \
Set should_continue to false and provide a rejection_reason for anything else — \
general chat, coding questions, math problems, or any off-topic request.

If should_continue is true, extract the profile. If false, set role, \
years_experience, current_skills, and career_goal to empty/zero defaults.

Return JSON with exactly these snake_case field names:
{"should_continue": bool, "rejection_reason": str, "role": str, \
"years_experience": int, "current_skills": [str], "career_goal": str}"""

    async def run(self, prompt: str) -> ProfileAnalystOutput:
        try:
            llm = _structured_llm(ProfileAnalystOutput)
            return await llm.ainvoke([
                SystemMessage(content=self._prompt),
                HumanMessage(content=prompt),
            ])
        except Exception as e:
            raise RoadmapAgentError(f"ProfileAnalyst failed: {e}") from e


class GoalStrategistAgent:
    _prompt = """\
You are a career growth strategist. Respond with valid JSON only.

Generate between 3 and 9 monthly sub-goals based on the complexity of the career goal \
and the user's starting experience level. A simple lateral move or already-senior profile \
may need 3–4 months; a major transition or junior starting point needs 6–9 months. \
Let the profile drive the length — do not pad or compress artificially.

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
- <2 yrs exp: fundamentals first, build confidence — lean toward more months
- 2–5 yrs exp: deepen expertise, add breadth
- 5+ yrs exp: leadership, specialization, influence — fewer months needed

Each month must have one clear theme and a one-sentence focus. \
Month N+1 must build on month N.

Return JSON with exactly these snake_case field names:
{"career_path": str, "sub_goals": [{"month": 1, "theme": str, "focus": str}, {"month": 2, "theme": str, "focus": str}, ...]}
"""

    async def run(self, profile: EmployeeProfile) -> SubGoals:
        try:
            llm = _structured_llm(SubGoals)
            content = (
                f"Role: {profile.role}\n"
                f"Experience: {profile.years_experience} years\n"
                f"Skills: {', '.join(profile.current_skills)}\n"
                f"Goal: {profile.career_goal}\n"
                f"Choose the right number of months (3–9) based on how far this person needs to go."
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

Design detailed learning modules for every month listed in the sub-goals you receive. \
Produce one curriculum entry per sub-goal month — no more, no fewer. \
The number of months is already decided; your job is to fill each one with content.

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
more advanced, leadership-oriented modules

Return JSON with exactly these snake_case field names:
{"months": [{"month": 1, "theme": str, "modules": [{"name": str, "topics": [str, str, str], "concepts": [str, str, str], "milestone": str}, {"name": str, "topics": [...], "concepts": [...], "milestone": str}]}, {"month": 2, ...}, ...]}
Each module must contain exactly these fields: "name" (str), "topics" (list of 3–5 strings), "concepts" (list of 3–5 strings), "milestone" (str).
"""

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
                f"Career path: {sub_goals.career_path}\n"
                f"Produce curriculum for exactly these {len(sub_goals.sub_goals)} months:\n\n"
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
# Career Roadmap: {career_goal}
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
