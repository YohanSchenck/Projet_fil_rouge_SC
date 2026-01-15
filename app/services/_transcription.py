import logging
from datetime import datetime
from pathlib import Path

from app.core import APICONFIG
from app.ressources import get_model
from app.schemas import Input, Prediction
from app.services.modules.audio import extract_audio, extract_audio_bytes
from app.services.modules.subtitles import generate_srt, merge_subtitles

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "video_output"


async def transcription(file_name: str, video_bytes: bytes,device: int = -1,embed: bool = False):
    logging.basicConfig(level=logging.INFO)

    #video_name = video_path.name

    #output_video = OUTPUT_DIR / (datetime.now().strftime("%Y%m%d")+file_name)

    audio_bytes = extract_audio_bytes(video_bytes)

    #audio_path = extract_audio(video_path)

    model = get_model(device)

    transcription = model.get_script_transcription(audio_bytes)
        
    srt_file = generate_srt(transcription, file_name)
    merge_subtitles(video_path, srt_file, output_video, embed)

    logging.info("Transcription done.")
    return transcription.get("text", ""), srt_file, output_video
