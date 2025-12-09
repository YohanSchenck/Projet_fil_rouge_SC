import math
from datetime import datetime, timedelta


def format_time(seconds: float)-> str:
    """ Convertit les secondes au format utilisé dans la transcription"""
    seconds2 = seconds
    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"

    print(str(timedelta(seconds=seconds2)))
    print(formatted_time)

    return formatted_time

format_time(120.9)
