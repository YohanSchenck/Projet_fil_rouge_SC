
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

    def get_script_transcription(self,audio_data):
        audio_input = {"raw": audio_data, "sampling_rate": 16000}
        return self._model(
        audio_input,
        chunk_length_s=28,
        batch_size=8,
        return_timestamps=True
    )

# Example of singleton usage to have a single model for all calls
# It would need to be improved in a multi users settings
@lru_cache
def get_model(device: int) -> Model:
    return Model(device)
