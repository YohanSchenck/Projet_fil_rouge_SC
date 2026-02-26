import asyncio
import logging
import time

import numpy as np
from app.ressources import ModelClient
from app.schemas.enums import ResponseType
from app.services.modules.audio import extract_audio_bytes
from app.services.modules.subtitles import (generate_srt_string,
                                            merge_subtitles_hard,
                                            merge_subtitles_soft)
from fastapi.concurrency import run_in_threadpool
from prometheus_client import Counter, Histogram

# Instanciation model 
inference_client = ModelClient()

# On garde le sémaphore pour ne pas saturer les workers Whisper
ai_semaphore = asyncio.Semaphore(3)

#Data Prometheus
TRANSCRIPTION_COUNT = Counter(
    'transcription_total', 
    'Nombre total de transcriptions réalisées', 
    ['status', 'response_type']
)

TRANSCRIPTION_LATENCY = Histogram(
    'transcription_duration_seconds', 
    'Temps de calcul de la transcription', 
    ['response_type']
)

MEDIA_DURATION_TOTAL = Counter(
    'media_duration_seconds_total', 
    'Somme totale de la durée des fichiers traités', 
    ['response_type']
)


async def transcription_service(
    file_bytes: bytes, 
    file_name: str, 
    response_type: ResponseType,
):
    logging.info(f"Start processing {file_name} for {response_type}")
    start_time = time.time()
    type_str = response_type.value

    try:
        # On délègue l'appel subprocess de FFmpeg au threadpool
        audio_bytes, media_duration = await run_in_threadpool(extract_audio_bytes, file_bytes)
        
        # 3. Inférence (Asynchrone + Sémaphore)
        async with ai_semaphore:
            logging.info(f"AI Slot acquired for {file_name}")
            result = await inference_client.get_script_transcription_remote(audio_bytes)

        duration = time.time() - start_time
        TRANSCRIPTION_COUNT.labels(status="success", response_type=type_str).inc()
        TRANSCRIPTION_LATENCY.labels(response_type=type_str).observe(duration)
        MEDIA_DURATION_TOTAL.labels(response_type=response_type.value).inc(media_duration)
        
        # 4. Traitement de la sortie
        if response_type == ResponseType.TEXT:
            raw_text = result.get("text", "").strip()
            return raw_text.encode("utf-8"), "text/plain", f"{file_name}.txt"
        else:
            srt_content = generate_srt_string(result)
            match response_type:
                case ResponseType.SRT:
                    return srt_content.encode('utf-8'), "application/x-subrip", f"{file_name}.srt"
                
                case ResponseType.VIDEO_METADATA:
                    video_out = await run_in_threadpool(merge_subtitles_soft, file_bytes, srt_content)
                    return video_out, "video/mp4", f"{file_name}_with_metadata.mp4"

                case ResponseType.VIDEO_EMBEDDED:
                    video_out = await run_in_threadpool(merge_subtitles_hard, file_bytes, srt_content)
                    return video_out, "video/mp4", f"embedded_{file_name}.mp4"
    
    except Exception as e:
        # En cas d'erreur :
        TRANSCRIPTION_COUNT.labels(status="error", response_type=type_str).inc()
        raise e
