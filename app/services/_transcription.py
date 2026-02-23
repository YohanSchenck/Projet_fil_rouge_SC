import asyncio
import io
import logging

import numpy as np
from app.ressources import ModelClient
from app.schemas.enums import ResponseType
from app.services.modules.audio import extract_audio_bytes
from app.services.modules.subtitles import (generate_srt_string,
                                            merge_subtitles_hard,
                                            merge_subtitles_soft)
from fastapi.concurrency import run_in_threadpool
from scipy.io import wavfile

# On garde le sémaphore pour ne pas saturer les workers Whisper
ai_semaphore = asyncio.Semaphore(3)


async def transcription_service(
    file_bytes: bytes, 
    file_name: str, 
    response_type: ResponseType,
    is_audio_file: bool = False
):
    logging.info(f"Start processing {file_name} for {response_type}")

    # On délègue l'appel subprocess de FFmpeg au threadpool
    audio_bytes = await run_in_threadpool(extract_audio_bytes, file_bytes)
    
    # 3. Inférence (Asynchrone + Sémaphore)
    inference_client = ModelClient()
    async with ai_semaphore:
        logging.info(f"AI Slot acquired for {file_name}")
        result = await inference_client.get_script_transcription_remote(audio_bytes)
    
    # 4. Traitement de la sortie
    if response_type == ResponseType.TEXT:
        raw_text = result.get("text", "").strip()
        return raw_text.encode("utf-8"), "text/plain", f"{file_name}.txt"

    srt_content = generate_srt_string(result)

    if response_type == ResponseType.SRT or is_audio_file:
        return srt_content.encode('utf-8'), "application/x-subrip", f"{file_name}.srt"

    if response_type == ResponseType.VIDEO_METADATA:
        # Soft subs : On délègue au threadpool car FFmpeg est appelé
        video_out = await run_in_threadpool(merge_subtitles_soft, file_bytes, srt_content)
        return video_out, "video/mp4", f"soft_{file_name}.mp4"

    if response_type == ResponseType.VIDEO_EMBEDDED:
        # Hard subs : TRÈS lourd, déléguer au threadpool est vital ici
        video_out = await run_in_threadpool(merge_subtitles_hard, file_bytes, srt_content)
        return video_out, "video/mp4", f"hard_{file_name}.mp4"

    return None, None, None
