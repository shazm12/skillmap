import logging
import uuid

from fastapi import APIRouter, HTTPException
from livekit.api import AccessToken, CreateAgentDispatchRequest, LiveKitAPI, VideoGrants

from app.config import dev_settings as settings

router = APIRouter(prefix="/voice", tags=["voice"])
logger = logging.getLogger(__name__)

_ROOM_NAME = "skillmap-tutor"
_AGENT_NAME = "SkillMap Tutor"


@router.get("/token")
async def get_voice_token():
    identity = f"user-{uuid.uuid4().hex[:8]}"
    token = (
        AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_grants(VideoGrants(room_join=True, room=_ROOM_NAME))
        .to_jwt()
    )

    try:
        async with LiveKitAPI(
            settings.LIVEKIT_URL,
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET,
        ) as lk:
            await lk.agent_dispatch.create_dispatch(
                CreateAgentDispatchRequest(room=_ROOM_NAME, agent_name=_AGENT_NAME)
            )
        logger.info("Agent dispatched to room %r for identity %r", _ROOM_NAME, identity)
    except Exception:
        logger.exception("Failed to dispatch agent to room %r", _ROOM_NAME)
        raise HTTPException(status_code=503, detail="Agent unavailable — could not dispatch to room")

    return {"token": token, "url": settings.LIVEKIT_URL}
