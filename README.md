# SkillMap

A multiagent career development platform for tech professionals. Describe your current role and goals — SkillMap builds a personalized 6-month learning roadmap and gives you a voice-powered tutor to work through it.

---

## What it does

**Roadmap Generator** — Submit a career goal prompt (e.g. "I'm a junior backend engineer and want to become a senior"). A multi-agent pipeline analyzes your profile, breaks the goal into milestones, designs a curriculum, and streams back a structured 6-month roadmap in real time.

**Voice Tutor** — A conversational AI tutor that answers questions about topics from your roadmap. Talks about software engineering, ML/AI, DevOps, product management, and tech leadership. Stays on topic — it redirects anything outside those domains.

---

## Tech stack

| Layer | Tools |
|---|---|
| Frontend | Next.js 16, React 19, Tailwind CSS v4, shadcn/ui |
| Voice UI | LiveKit Components React, `@livekit/components-react` |
| Backend | FastAPI, Python 3.13, uv |
| Roadmap pipeline | LangGraph, LangChain, Groq (OpenAI OSS 20B) |
| Voice pipeline | LiveKit Agents 1.6.5, Deepgram STT (nova-3), Groq LLM, Cartesia TTS, Silero VAD |
| Containerization | Docker, python:3.13-slim, uv for dependency management |
| Deployment | Railway (backend), Vercel (frontend) |

---

## Architecture

```
Browser
  ├── /roadmap   → RoadmapChat  → POST /api/roadmap/stream (SSE)
  └── /tutor     → VoiceAgent   → GET  /api/voice/token
                                       └── LiveKit Room (WebRTC)
                                              └── TutorAgent worker
```

The backend is a single FastAPI app with two responsibilities:
1. Serves the roadmap SSE stream
2. Mints LiveKit JWT tokens and explicitly dispatches the agent to the room

The voice agent runs as a subprocess spawned by FastAPI at startup, registered with the LiveKit server in explicit dispatch mode.

---

## Roadmap pipeline

Five LangGraph nodes run in sequence:

```
ProfileAnalyst → [guardrail] → GoalStrategist → CurriculumDesigner → Personalizer
                     ↓ (rejected)
                   Reject node → SSE type: "rejection" (amber UI)
```

- **ProfileAnalyst** — extracts role, experience, skills, and career goal from free-text. Rejects prompts outside supported paths (SWE, ML/AI, PM, Tech Lead).
- **GoalStrategist** — breaks the goal into 6-month sub-goals.
- **CurriculumDesigner** — maps sub-goals to learning topics with resources.
- **Personalizer** — rewrites the curriculum in markdown to match the user's current skill level.

Output streams token-by-token over SSE. Rejections send `"type": "rejection"` so the frontend renders an amber warning instead of a roadmap.
> **Note:** The roadmap is generated in Markdown format, allowing our frontend to parse and render it with `react-markdown` for consistent, feature-rich formatting.

---

## Voice agent pipeline

```
User mic → Deepgram STT → Silero VAD → TurnDetector → Groq LLM → Cartesia TTS → Speaker
```

- **Silero VAD** — prewarmed on startup, filters noise from actual speech.
- **TurnDetector** — decides when the user has finished speaking before forwarding to LLM.
- **Empty transcript guard** — transcripts shorter than 3 chars are dropped; agent asks the user to repeat instead of sending garbage to the LLM.
- **Topic guardrail** — baked into the system prompt; the agent refuses non-technical questions with a fixed redirect message.
- **Participant disconnect handler** — logs when the user leaves so the session closes cleanly.

---

## Deployment

**Backend → Railway**

The backend ships as a Docker container:

```dockerfile
FROM python:3.13-slim
# uv for fast, reproducible installs
RUN uv sync --frozen --no-dev
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Railway detects the Dockerfile and builds automatically on push. Set these env vars in the Railway dashboard:

```
GROQ_API_KEY
LIVEKIT_URL
LIVEKIT_API_KEY
LIVEKIT_API_SECRET
GROQ_MODEL
```

**Frontend → Vercel**

Connect the GitHub repo, set the root directory to `frontend`, and add:

```
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

Vercel builds and deploys on push.

---

## Local setup

```bash
# Backend
cd backend
cp .env.example .env   # fill in keys
uv sync
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
or
./run.sh # shell script to start the dev server

# Frontend
cd frontend
npm install
npm run dev            # http://localhost:3000
```

> **Note:** `CORS_ORIGINS` in `.env` must be a JSON array if set:
> `CORS_ORIGINS=["http://localhost:3000"]`
