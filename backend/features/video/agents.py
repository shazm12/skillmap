from backend.features.video.schemas import Storyboard, VideoRequest


class ScriptWriterAgent:
    """
    Generates a ~60 second explanation script (~160 words)
    for a given concept from the roadmap.
    """

    async def run(self, request: VideoRequest) -> str:
        raise NotImplementedError


class StoryboardAgent:
    """
    Splits the script into scenes with visual layout
    descriptions for each animated slide.
    """

    async def run(self, script: str) -> Storyboard:
        raise NotImplementedError


class NarratorAgent:
    """
    Converts the script to audio using Kokoro ONNX TTS.
    Returns path to generated .wav file.
    """

    async def run(self, script: str, output_path: str) -> str:
        raise NotImplementedError


class AnimatorAgent:
    """
    Renders animated slide frames from the storyboard
    using Pillow + MoviePy. Returns path to silent .mp4.
    """

    async def run(self, storyboard: Storyboard, output_path: str) -> str:
        raise NotImplementedError


class EditorAgent:
    """
    Merges the audio (.wav) and silent video (.mp4)
    into a final .mp4 using FFmpeg.
    """

    async def run(self, video_path: str, audio_path: str, output_path: str) -> str:
        raise NotImplementedError
