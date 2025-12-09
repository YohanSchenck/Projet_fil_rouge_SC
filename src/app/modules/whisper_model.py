import logging
import torch
from transformers import pipeline


def load_whisper(device: int = -1):
    """Charge un modèle Whisper dans une pipeline"""
    logging.info("Loading Whisper model...")
    return pipeline(
        "automatic-speech-recognition",
        "openai/whisper-tiny.en",
        torch_dtype=torch.float16,
        device=device
    )