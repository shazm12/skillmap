"""
Animated slide renderer using Pillow + MoviePy.
Generates per-scene frames and compiles them into a silent .mp4.
"""
from app.features.video.schemas import Storyboard


class SlideAnimator:
    RESOLUTION = (1280, 720)
    FPS = 24
    BG_COLOR = (15, 15, 25)
    TEXT_COLOR = (240, 240, 240)
    ACCENT_COLOR = (99, 102, 241)  # indigo

    def render_scene(self, scene: dict, output_dir: str) -> list[str]:
        """Render a single scene into a list of frame image paths."""
        raise NotImplementedError

    def compile_video(self, frame_dirs: list[str], output_path: str) -> str:
        """Compile all scene frames into a silent .mp4. Returns output path."""
        raise NotImplementedError

    def render(self, storyboard: Storyboard, output_path: str) -> str:
        """Full render pipeline: scenes → frames → silent .mp4."""
        raise NotImplementedError
