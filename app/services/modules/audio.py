import logging
from pathlib import Path

import ffmpeg


def extract_audio(input_video: Path) -> Path:
    """Extrait l'audio d'une vidéo en utilisant ffmpeg"""
    extracted_audio = input_video.with_suffix(".wav")
    logging.info(f"Extracting audio: {extracted_audio}")

    stream = ffmpeg.input(str(input_video))
    stream = ffmpeg.output(stream, str(extracted_audio))

    ffmpeg.run(stream, overwrite_output=True)
    return extracted_audio
