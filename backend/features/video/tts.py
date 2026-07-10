"""
Kokoro ONNX TTS wrapper.
Handles text-to-speech conversion locally with minimal latency.
"""


class KokoroTTS:
    def __init__(self):
        # TODO: initialize kokoro-onnx model
        self.model = None
        self.voice = "af_heart"  # default voice

    def load(self):
        raise NotImplementedError

    def synthesize(self, text: str, output_path: str) -> str:
        """Convert text to speech and save as .wav. Returns output path."""
        raise NotImplementedError
