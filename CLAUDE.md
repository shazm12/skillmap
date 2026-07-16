# SkillMap — Claude Code Context

A multiagent career development platform. Two features: a **roadmap generator** (LangGraph pipeline → SSE stream) and a **voice tutor** (LiveKit Agents, WebRTC).

## Project layout

```
cb-project/
├── backend/          # FastAPI app + both pipelines
│   ├── app/
│   │   ├── config.py                        # pydantic-settings, all env vars
│   │   ├── main.py                          # FastAPI app, lifespan, CORS
│   │   ├── pipelines/
│   │   │   ├── roadmap/
│   │   │   │   ├── agents.py                # 4 LangChain agents (ProfileAnalyst, GoalStrategist, CurriculumDesigner, Personalizer)
│   │   │   │   ├── graph.py                 # LangGraph 5-node workflow
│   │   │   │   └── schemas.py               # Pydantic I/O schemas with validation constraints
│   │   │   └── voice_agent/
│   │   │       └── agent.py                 # LiveKit TutorAgent worker
│   │   └── routes/
│   │       ├── roadmap_router.py            # POST /api/roadmap/stream (SSE)
│   │       └── voice_router.py              # GET /api/voice/token
│   ├── .env.example                         # copy to .env and fill in keys
│   ├── Dockerfile
│   └── run.sh                               # dev start script
└── frontend/         # Next.js 16, React 19, Tailwind v4, shadcn/ui
    ├── app/
    │   ├── roadmap/page.tsx                 # roadmap generator page
    │   └── tutor/page.tsx                   # voice tutor page
    └── components/
        ├── roadmap/RoadmapChat.tsx          # SSE consumer + react-markdown renderer
        └── tutor/VoiceAgent.tsx             # LiveKit WebRTC UI
```

## Running locally

```bash
# Backend
cd backend
cp .env.example .env   # fill in all keys
./run.sh               # starts uvicorn + spawns voice agent subprocess

# Frontend
cd frontend
npm install
npm run dev            # http://localhost:3000
```

## Required env vars (backend/.env)

| Var | Where to get it |
|---|---|
| `GROQ_API_KEY` | console.groq.com |
| `GROQ_MODEL` | e.g. `qwen/qwen3-32b` or `openai/gpt-oss-20b` |
| `LIVEKIT_URL` | LiveKit Cloud dashboard (wss://...) |
| `LIVEKIT_API_KEY` | LiveKit Cloud dashboard |
| `LIVEKIT_API_SECRET` | LiveKit Cloud dashboard |
| `DEEPGRAM_API_KEY` | deepgram.com |
| `CARTESIA_API_KEY` | cartesia.ai |

**`CORS_ORIGINS` must be a JSON array if set:** `CORS_ORIGINS=["http://localhost:3000"]`. An empty value (`CORS_ORIGINS=`) causes a pydantic-settings parse error at startup — either set it correctly or remove the line.

Frontend env (frontend/.env.local):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Non-obvious architecture decisions

**Voice agent is a subprocess, not a separate process.** `main.py` lifespan spawns `app.pipelines.voice_agent.agent` via `asyncio.create_subprocess_exec`. You do not start it manually — starting `uvicorn` starts it automatically.

**Voice agent uses explicit dispatch mode.** `WorkerOptions(agent_name="SkillMap Tutor")` registers the worker in explicit dispatch mode with LiveKit. The `/api/voice/token` endpoint must call `lk.agent_dispatch.create_dispatch()` after minting the JWT — otherwise the agent is never assigned to the room.

**Structured LLM output uses `json_mode`, not tool calling.** `ChatGroq.with_structured_output(schema, method="json_mode")` is used throughout the roadmap pipeline. Tool calling is less reliable on Groq-hosted models.

**6-month enforcement is two-layered.** (1) Prompt level: `CRITICAL RULE` in `GoalStrategistAgent._prompt` and `CurriculumDesignerAgent._prompt` instructs the LLM to always output exactly 6 months regardless of what the user says. (2) Schema level: `min_length=6, max_length=6` on `SubGoals.sub_goals` and `Curriculum.months` in `schemas.py` — Pydantic rejects any response with the wrong count, which surfaces as `RoadmapAgentError`.

**SSE rejection type.** When `ProfileAnalyst` sets `should_continue=False`, the graph routes to a `_reject` node that yields `{"type": "rejection", "content": "..."}`. The frontend detects this and renders an amber warning instead of the roadmap. Any change to this field name must be mirrored in the frontend SSE consumer.

**Empty transcript guard.** `_MIN_TRANSCRIPT_CHARS = 2` in `agent.py` — transcripts shorter than 2 chars are dropped in `on_user_turn_completed` without forwarding to the LLM.

## Roadmap pipeline flow

```
POST /api/roadmap/stream
  └── LangGraph
        ProfileAnalyst (extracts profile + guardrail)
          ├── rejected → _reject node → SSE type:"rejection"
          └── continue → GoalStrategist → CurriculumDesigner → Personalizer → SSE stream
```

All agents wrap failures in `RoadmapAgentError`. The SSE generator catches this and yields `{"error": "..."}` rather than crashing the stream.

## Package management

Backend uses `uv`. Never use `pip install` directly.

```bash
uv add <package>      # add dependency
uv sync               # install all deps
uv run <command>      # run in venv
```

## Deployment

- **Backend → Railway**: Dockerfile is at `backend/Dockerfile`. Railway auto-detects it. Set all env vars in the Railway dashboard.
- **Frontend → Vercel**: Set root directory to `frontend`. Add `NEXT_PUBLIC_API_URL` pointing to the Railway URL.

## Engineering conventions (strict — all agents)

- Commit messages follow conventional-commit style: imperative subject (`feat: ...`, `fix: ...`, `refactor: ...`), body says *why* not *what*. No vague messages like "updates" or "fixes stuff".
- DRY: no duplicating logic, schema, or config across frontend/backend/data-layer — extract one shared source of truth instead.
- SOLID where it genuinely reduces coupling (small, single-responsibility modules, code against interfaces at real seams) — don't force it where it's just ceremony.
- Don't default to agreeing with the developer. Verify non-trivial technical claims against authoritative sources (official docs, current library/API references, etc.) before confirming them, and say so plainly — with the source — when the developer's assumption turns out to be wrong.
- For documentation lookups, always use the context7 MCP first if it's connected; fall back to normal web search only if it isn't or doesn't have the answer.
- Never estimate cost/timelines as if a human developer were doing the work. This project is built by AI agents — estimates should reflect realistic AI-driven development speed, not human sprint/story-point conventions.
