import asyncio
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.features.video.agents import (
    AnimatorAgent,
    EditorAgent,
    NarratorAgent,
    ScriptWriterAgent,
    StoryboardAgent,
)
from app.features.video.schemas import Storyboard, VideoRequest


class VideoState(TypedDict):
    request: VideoRequest
    script: str
    storyboard: Storyboard
    audio_path: str
    silent_video_path: str
    final_video_path: str


async def _parallel_narrator_animator(state: VideoState) -> dict:
    """Run Narrator and Animator in parallel to minimize latency."""
    narrator = NarratorAgent()
    animator = AnimatorAgent()

    audio_path, silent_video_path = await asyncio.gather(
        narrator.run(state["script"], "output/audio/narration.wav"),
        animator.run(state["storyboard"], "output/videos/silent.mp4"),
    )

    return {"audio_path": audio_path, "silent_video_path": silent_video_path}


def build_video_graph() -> StateGraph:
    script_writer = ScriptWriterAgent()
    storyboard_agent = StoryboardAgent()
    editor = EditorAgent()

    graph = StateGraph(VideoState)

    graph.add_node("script_writer", lambda s: {"script": script_writer.run(s["request"])})
    graph.add_node("storyboard", lambda s: {"storyboard": storyboard_agent.run(s["script"])})
    graph.add_node("narrator_animator", _parallel_narrator_animator)
    graph.add_node(
        "editor",
        lambda s: {
            "final_video_path": editor.run(
                s["silent_video_path"], s["audio_path"], "output/videos/final.mp4"
            )
        },
    )

    graph.set_entry_point("script_writer")
    graph.add_edge("script_writer", "storyboard")
    graph.add_edge("storyboard", "narrator_animator")
    graph.add_edge("narrator_animator", "editor")
    graph.add_edge("editor", END)

    return graph.compile()
