import io
import logging
import time

import numpy as np
from app.ressources import ModelClient
from app.schemas.enums import ResponseType
from app.services.modules.audio import extract_audio_bytes
from app.services.modules.subtitles import (generate_srt_string,
                                            merge_subtitles_hard,
                                            merge_subtitles_soft)
from scipy.io import wavfile


async def transcription_service(
    file_bytes: bytes, 
    file_name: str, 
    response_type: ResponseType,
    is_audio_file: bool = False
):
    """
    Orchestre le process : Bytes -> Audio -> Texte -> Résultat formaté
    """

    logging.info(f"Start processing {file_name} for {response_type}")

    # 1. Préparer l'audio pour le modèle
    if is_audio_file:
        # Si c'est déjà un WAV/MP3, on peut tenter de le passer direct ou le convertir en 16k mono
        # Pour simplifier, on utilise la même moulinette ffmpeg qui nettoie tout
        audio_bytes = extract_audio_bytes(file_bytes)
    else:
        # Si c'est une vidéo, on extrait l'audio
        audio_bytes = extract_audio_bytes(file_bytes)
    
    # 2. Conversion Bytes WAV -> NumPy (Indispensable pour Hugging Face in-memory)
    with io.BytesIO(audio_bytes) as audio_file:
        samplerate, data = wavfile.read(audio_file)
        # Normalisation : transformer les entiers 16-bit en flottants entre -1 et 1
        audio_np = data.astype(np.float32) / 32768.0

    # 3. Inférence (Modèle chargé en mémoire)
    # Note: get_model(-1) suppose CPU, ajuster selon ta config
    #model = get_model(-1) 
    inference_client = ModelClient()

    # Attention: ton model.get_script_transcription doit accepter des bytes ou un np.array
    # Si ton modèle attend un fichier path, il faudra utiliser io.BytesIO
    # Supposons qu'il accepte les bytes bruts du WAV :
    #result = model.get_script_transcription(audio_np)
    result = await inference_client.get_script_transcription_remote(audio_bytes)
    
    # 4. Traitement de la sortie
    if response_type == ResponseType.TEXT:
            raw_text = result.get("text", "").strip()
            # On convertit le texte en bytes pour le téléchargement
            return raw_text.encode("utf-8"), "text/plain", f"{file_name}.txt"

    # Génération du SRT en string
    srt_content = generate_srt_string(result)

    if response_type == ResponseType.SRT:
        # On encode en bytes pour le retour fichier
        return srt_content.encode('utf-8'), "application/x-subrip", f"{file_name}.srt"

    # Si on est ici, c'est de la vidéo (Soft ou Hard subs)
    if is_audio_file:
        # Impossible de faire de la vidéo embedded sur un fichier audio source
        # Fallback sur SRT
        return srt_content.encode('utf-8'), "application/x-subrip", f"{file_name}.srt"

    if response_type == ResponseType.VIDEO_METADATA:
        # Soft subs (rapide)
        video_out = merge_subtitles_soft(file_bytes, srt_content)
        return video_out, "video/mp4", f"soft_{file_name}.mp4"

    if response_type == ResponseType.VIDEO_EMBEDDED:
        # Hard subs (lent)
        video_out = merge_subtitles_hard(file_bytes, srt_content)
        return video_out, "video/mp4", f"hard_{file_name}.mp4"

    return None, None, None
