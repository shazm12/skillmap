import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.pipelines.roadmap.agents import RoadmapAgentError
from app.pipelines.roadmap.schemas import RoadmapRequest

router = APIRouter(prefix="/roadmap", tags=["roadmap"])
logger = logging.getLogger(__name__)


@router.post("/generate")
async def generate_roadmap(request: RoadmapRequest, req: Request):
    graph = req.app.state.roadmap_graph

    async def token_stream():
        try:
            final_state = {}

            async for event in graph.astream_events(
                {"prompt": request.prompt},
                version="v2",
            ):
                if (
                    event["event"] == "on_chat_model_stream"
                    and event.get("metadata", {}).get("langgraph_node") == "personalizer"
                ):
                    chunk = event["data"]["chunk"]
                    if not chunk.content:
                        continue
                    yield f"data: {json.dumps({'token': chunk.content})}\n\n"

                elif event["event"] == "on_chain_end" and event.get("name") == "LangGraph":
                    final_state = event["data"].get("output", {})

            if final_state.get("should_continue") is False:
                rejection = final_state.get("final_roadmap", "")
                yield f"data: {json.dumps({'token': rejection, 'type': 'rejection'})}\n\n"

            yield "data: [DONE]\n\n"

        except RoadmapAgentError as e:
            logger.exception("Agent pipeline failed — prompt: %r", request.prompt)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        except Exception as e:
            logger.exception("Unexpected error in roadmap stream — prompt: %r", request.prompt)
            yield f"data: {json.dumps({'error': f'Unexpected error: {str(e)}'})}\n\n"

    return StreamingResponse(token_stream(), media_type="text/event-stream")
