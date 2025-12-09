import logging
from datetime import datetime
from pathlib import Path

from app.modules.audio import extract_audio
from app.modules.subtitles import generate_srt, merge_subtitles
from app.modules.whisper_model import load_whisper


def main(video_path: Path,device: int = -1,embed: bool = False):
    logging.basicConfig(level=logging.INFO)

    video_name = video_path.name

    #input_video = Path("video_input/"+video_name)
    output_video = Path("video_output/"+datetime.now().strftime("%Y%m%d")+video_name)

    audio_path = extract_audio(video_path)
    whisper = load_whisper(device)

    transcription = whisper(
        str(audio_path),
        chunk_length_s=28,
        return_timestamps=True
    )
    
    
    srt_file = generate_srt(transcription, video_name)
    merge_subtitles(video_path, srt_file, output_video, embed)

    logging.info("Transcription done.")
    return transcription.get("text", "")






