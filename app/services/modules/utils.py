import math


def format_time(seconds: float) -> str:
    """ Convertit les secondes au format SRT standard (HH:MM:SS,mmm) """
    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    
    # Correction ici : 02d pour les secondes
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    return formatted_time
