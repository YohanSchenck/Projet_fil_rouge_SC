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

import io
import subprocess


def extract_audio_bytes(video_bytes: bytes) -> bytes:
    """
    Extrait un WAV depuis une vidéo en mémoire via FFmpeg.
    """
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-i", "pipe:0",
            "-vn",          # pas de vidéo
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            "pipe:1"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    audio_bytes, err = process.communicate(video_bytes)

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed: {err.decode()}")

    return audio_bytes
