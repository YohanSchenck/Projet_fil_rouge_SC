
from functools import lru_cache
from pathlib import Path

import torch
from transformers import pipeline


class Model:

    def __init__(self, device: int):
        """Charge un modèle Whisper""" 
        self._model = pipeline(
            "automatic-speech-recognition",
            "openai/whisper-tiny.en",
            torch_dtype=torch.float16,
            device=device
        )

    def get_script_transcription(self,audio_path : bytes):
        return self._model(
        str(audio_path),
        chunk_length_s=28,
        return_timestamps=True
    )

# Example of singleton usage to have a single model for all calls
# It would need to be improved in a multi users settings
@lru_cache
def get_model(device: int) -> Model:
    return Model(device)
