import logging
from datetime import datetime
from pathlib import Path

import ffmpeg

from .utils import format_time


def generate_srt(transcription: dict, video_name: str) -> Path:
    text = ""
    offset = 0

    transcription_output_path = Path("sous-titres/"+datetime.now().strftime("%Y%m%d")+video_name+".srt")

    for index, chunk in enumerate(transcription["chunks"]):
        start = offset + chunk["timestamp"][0]
        end = offset + chunk["timestamp"][1]

        if start > end:
            offset += 28
            continue

        text += (
            f"{index + 1}\n"
            f"{format_time(start)} --> {format_time(end)}\n"
            f"{chunk['text'].strip()}\n\n"
        )

    transcription_output_path.write_text(text, encoding="utf-8")
    logging.info(f"SRT generated: {transcription_output_path}")
    return transcription_output_path


def merge_subtitles(input_video: Path, subtitle_file: Path,
                    output_video: Path, embed: bool = False):
    logging.info("Merging subtitles into video...")

    video = ffmpeg.input(str(input_video))

    if not embed:
        subs = ffmpeg.input(str(subtitle_file))
        stream = ffmpeg.output(
            video,
            subs,
            str(output_video),
            **{"c": "copy", "c:s": "mov_text"}
        )
    else:
        stream = ffmpeg.output(
            video,
            str(output_video),
            vf=f"subtitles={str(subtitle_file)}"
        )

    ffmpeg.run(stream, overwrite_output=True)
