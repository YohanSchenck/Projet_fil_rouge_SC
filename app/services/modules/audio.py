import logging
import re
import subprocess
from pathlib import Path


def extract_audio_bytes(video_bytes: bytes) -> tuple[bytes, float]:
    """
    Extrait la piste audio d'une vidéo (en bytes) vers du WAV (en bytes)
    via les pipes FFmpeg, sans écrire sur le disque.
    """
    try:
        # On lance ffmpeg en écoutant stdin (pipe:0) et écrivant sur stdout (pipe:1)
        process = subprocess.Popen(
            [
                "ffmpeg",
                "-threads", "1",        # Utiliser tous les coeurs
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
        stderr_text = err.decode()
        
        if process.returncode != 0:
            logging.error(f"FFmpeg Error: {err.decode()}")
            raise RuntimeError("Erreur lors de l'extraction audio via FFmpeg.")

        duration = 0.0
        match = re.search(r"Duration:\s(\d+):(\d+):(\d+\.\d+)", stderr_text)
        if match:
            h, m, s = match.groups()
            duration = int(h) * 3600 + int(m) * 60 + float(s)

        return audio_output,duration

    except Exception as e:
        logging.error(f"Exception in extract_audio_bytes: {str(e)}")
        raise
