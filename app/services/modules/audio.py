import logging
import subprocess
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


def extract_audio_bytes(video_bytes: bytes) -> bytes:
    """
    Extrait la piste audio d'une vidéo (en bytes) vers du WAV (en bytes)
    via les pipes FFmpeg, sans écrire sur le disque.
    """
    try:
        # On lance ffmpeg en écoutant stdin (pipe:0) et écrivant sur stdout (pipe:1)
        process = subprocess.Popen(
            [
                "ffmpeg",
                "-threads", "0",        # Utiliser tous les coeurs
                "-i", "pipe:0",         # Entrée depuis la RAM
                "-vn",                  # Pas de vidéo
                "-acodec", "pcm_s16le", # Format WAV standard pour l'IA
                "-ar", "16000",         # 16kHz (requis par Whisper souvent)
                "-ac", "1",             # Mono
                "-f", "wav",            # Format conteneur
                "pipe:1"                # Sortie vers la RAM
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # On envoie les bytes de la vidéo et on récupère le résultat
        audio_output, err = process.communicate(input=video_bytes)

        if process.returncode != 0:
            logging.error(f"FFmpeg Error: {err.decode()}")
            raise RuntimeError("Erreur lors de l'extraction audio via FFmpeg.")

        return audio_output

    except Exception as e:
        logging.error(f"Exception in extract_audio_bytes: {str(e)}")
        raise
