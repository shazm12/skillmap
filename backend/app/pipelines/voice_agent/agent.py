from dotenv import load_dotenv
load_dotenv()

import logging
from livekit.agents import Agent, AgentSession, JobContext, JobProcess, WorkerOptions, cli
from livekit.agents.inference import TurnDetector
from livekit.agents import llm
from livekit.plugins import deepgram, groq, cartesia, silero

from app.config import dev_settings as settings

logger = logging.getLogger(__name__)

_MIN_TRANSCRIPT_CHARS = 3


class TutorAgent(Agent):

    def __init__(self):
        super().__init__(
            instructions="""\
You are a learning coach for tech professionals working through a 6-month career roadmap. \
You ONLY answer questions about technical topics from these four career paths:
- Senior Software Engineer: distributed systems, APIs, CI/CD, system design, code review, mentoring
- ML/AI Engineer: linear algebra, neural networks, Transformers, MLOps, RAG, LLMs, vector databases
- Product Manager: discovery, PRDs, OKRs, prioritization, roadmapping, go-to-market, A/B testing
- Tech Lead: architecture decisions, ADRs, team topologies, DORA metrics, engineering culture, hiring

Guardrail — apply before every response:
If the question is not about software engineering, ML/AI, DevOps, product management, \
or tech leadership concepts, respond with exactly: \
"I can only help with technical career topics. Ask me about something from your roadmap — \
like system design, machine learning, or product strategy." Then stop. Do not answer.

Rules for allowed questions — follow strictly:
- Respond in 2 to 3 short sentences only. Never exceed this.
- Use plain conversational language. No bullet points, no markdown, no lists.
- Always end with one short follow-up question to check understanding.
- Use a simple analogy when explaining a complex concept."""
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Greet the user warmly, introduce yourself as their learning coach, and ask what concept or topic they'd like to explore today."
        )

    async def on_user_turn_completed(
        self, turn_ctx: llm.ChatContext, new_message: llm.ChatMessage
    ) -> None:
        transcript = (new_message.text_content or "").strip()

        if len(transcript) < _MIN_TRANSCRIPT_CHARS:
            logger.warning("Received empty or garbage transcript, skipping LLM call")
            # Clear content so the session does not forward it to the LLM
            new_message.content = []
            await self.session.say(
                "I didn't quite catch that. Could you say it again?",
                allow_interruptions=True,
            )


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    def on_participant_disconnected(participant):
        logger.info("Participant disconnected: %s — session will close", participant.identity)

    ctx.room.on("participant_disconnected", on_participant_disconnected)

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=groq.LLM(model=settings.GROQ_MODEL, max_completion_tokens=200),
        tts=cartesia.TTS(),
        vad=ctx.proc.userdata["vad"],
        turn_detection=TurnDetector(),
    )

    try:
        await session.start(agent=TutorAgent(), room=ctx.room)
    except Exception:
        logger.exception("AgentSession failed to start")
        raise


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm, agent_name="SkillMap Tutor"))
