import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.pipelines.roadmap.agents import RoadmapAgentError
from app.pipelines.roadmap.schemas import RoadmapRequest

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.post("/generate")
async def generate_roadmap(request: RoadmapRequest, req: Request):
    graph = req.app.state.roadmap_graph

    async def token_stream():
        try:
            in_thinking = False
            buffer = ""

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

                    buffer += chunk.content

                    if not in_thinking:
                        if "<think>" in buffer:
                            pre = buffer[:buffer.index("<think>")]
                            if pre:
                                yield f"data: {json.dumps({'token': pre})}\n\n"
                            buffer = ""
                            in_thinking = True
                        else:
                            yield f"data: {json.dumps({'token': buffer})}\n\n"
                            buffer = ""
                    else:
                        if "</think>" in buffer:
                            buffer = buffer[buffer.index("</think>") + len("</think>"):]
                            in_thinking = False

            yield "data: [DONE]\n\n"

        except RoadmapAgentError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': f'Unexpected error: {str(e)}'})}\n\n"

    return StreamingResponse(token_stream(), media_type="text/event-stream")
