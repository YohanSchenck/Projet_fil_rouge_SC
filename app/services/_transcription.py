import logging
from datetime import datetime
from pathlib import Path

from app.core import APICONFIG
from app.ressources import get_model
from app.schemas import Features, Prediction
from app.services.modules.audio import extract_audio
from app.services.modules.subtitles import generate_srt, merge_subtitles

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "video_output"


async def single_prediction(features : Features) -> Prediction:
    model = get_model(APICONFIG.model_path)
    # TODO : get your model and its predict method
    result = model.predict(features.age, features.sexe)
    return Prediction(result=result)



async def transciption(video_path: Path,device: int = -1,embed: bool = False):
    logging.basicConfig(level=logging.INFO)

    video_name = video_path.name

    output_video = OUTPUT_DIR / (datetime.now().strftime("%Y%m%d")+video_name)

    audio_path = extract_audio(video_path)

    model = get_model(device)

    transcription = model.get_script_transcription(audio_path)
        
    srt_file = generate_srt(transcription, video_name)
    merge_subtitles(video_path, srt_file, output_video, embed)

    logging.info("Transcription done.")
    return transcription.get("text", "")
