from dotenv import load_dotenv
load_dotenv()

from livekit.agents import Agent, AgentSession, JobContext, JobProcess, WorkerOptions, cli
from livekit.agents.turn_detection import MultilingualModel
from livekit.plugins import deepgram, groq, cartesia, silero



class TutorAgent(Agent):
   
    def __init__(self):
        super().__init__(
            instructions="""\
You are a learning coach for tech professionals working through a 6-month career roadmap. \
Answer questions about topics and concepts from their roadmap across these four paths: \
Senior Software Engineer (distributed systems, APIs, CI/CD, system design, mentoring), \
ML/AI Engineer (linear algebra, neural networks, Transformers, MLOps, RAG, LLMs), \
Product Manager (discovery, PRDs, OKRs, prioritization, roadmapping, go-to-market), \
Tech Lead (architecture decisions, team topologies, DORA metrics, engineering culture).

Rules — follow strictly:
- Respond in 2 to 3 short sentences only. Never exceed this.
- Use plain conversational language. No bullet points, no markdown, no lists.
- Always end with one short follow-up question to check understanding.
- Use a simple analogy when explaining a complex concept."""
        )
   
    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Greet the user warmly, introduce yourself as their learning coach, and ask what concept or topic they'd like to explore today."
        )
       
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    await ctx.connect()
   
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=groq.LLM(model="qwen/qwen3-32b", max_tokens=200),
        tts=cartesia.TTS(),
        vad=ctx.proc.userdata["vad"],
        turn_detection=MultilingualModel(),
    )

    await session.start(agent=TutorAgent(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm, agent_name="SkillMap Tutor"))
