from enum import Enum


class ResponseType(str, Enum):
    TEXT = "text"              # Texte uniquement
    SRT = "srt"                # Fichier sous-titre uniquement
    VIDEO_EMBEDDED = "video_hard" # Vidéo avec sous-titres incrustés (pixels)
    VIDEO_METADATA = "video_soft" # Vidéo avec flux sous-titre (activable/désactivable)
