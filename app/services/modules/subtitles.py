import logging
import os
import subprocess
import tempfile

from .utils import format_time  # Assure-toi que cette fonction existe


def generate_srt_string(transcription: dict) -> str:
    """Génère le contenu SRT sous forme de chaîne de caractères."""
    text_content = ""
    segments = transcription.get("segments", [])

    if not segments:
        logging.warning("Aucun segment trouvé dans la transcription du serveur d'inférence.")
        return ""

    for index, segment in enumerate(segments):
        # Le serveur d'inférence fournit directement 'start' et 'end' en secondes (float)
        start = segment.get("start", 0.0)
        end = segment.get("end", start + 2.0) # Fallback de 2s si 'end' est absent
        text = segment.get("text", "").strip()

        # Construction du bloc SRT avec l'index, le temps formaté et le texte
        text_content += (
            f"{index + 1}\n"
            f"{format_time(start)} --> {format_time(end)}\n"
            f"{text}\n\n"
        )
        
    return text_content

def merge_subtitles_soft(video_bytes: bytes, srt_content: str) -> bytes:
    """
    AJOUT DE METADATA (Soft Subs).
    Incorpore le SRT comme un flux de texte dans le conteneur MP4 (activable/désactivable).
    Tout se fait en mémoire via Pipes.
    """
    # Pour le soft sub, ffmpeg a besoin de deux entrées pipe
    # C'est complexe avec subprocess simple car il n'y a qu'un stdin.
    # Astuce : On écrit le SRT dans un fichier temporaire (très léger), 
    # mais la vidéo reste en RAM.
    
    with tempfile.NamedTemporaryFile(suffix=".srt", delete=False, mode="w", encoding="utf-8") as tmp_srt:
        tmp_srt.write(srt_content)
        srt_path = tmp_srt.name

    try:
        cmd = [
            "ffmpeg",
            "-i", "pipe:0",           # Entrée 0 : Vidéo (RAM)
            "-i", srt_path,           # Entrée 1 : SRT (Fichier Temp)
            "-c:v", "copy",           # Copie vidéo sans réencodage (Rapide)
            "-c:a", "copy",           # Copie audio sans réencodage
            "-c:s", "mov_text",       # Format sous-titre pour MP4
            "-map", "0",              # Mapper tout le fichier 0
            "-map", "1",              # Mapper le fichier 1
            "-f", "mp4",              # Forcer le format MP4
            "-movflags", "frag_keyframe+empty_moov", # Important pour le streaming/pipe
            "pipe:1"
        ]

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out_bytes, err = process.communicate(input=video_bytes)

        if process.returncode != 0:
            logging.error(f"Soft Merge Error: {err.decode()}")
            raise RuntimeError("Erreur fusion sous-titres metadata.")
        
        return out_bytes
    finally:
        # Nettoyage immédiat du fichier SRT
        if os.path.exists(srt_path):
            os.remove(srt_path)

def merge_subtitles_hard(video_bytes: bytes, srt_content: str) -> bytes:
    """
    INCRUSTATION VIDEO (Hard Subs / Embedded).
    Réencode la vidéo pour brûler les pixels. Très couteux en CPU.
    """
    with tempfile.NamedTemporaryFile(suffix=".srt", delete=False, mode="w", encoding="utf-8") as tmp_srt:
        tmp_srt.write(srt_content)
        srt_path = tmp_srt.name
    
    # Correction path pour ffmpeg (caractères spéciaux sous Windows/Linux parfois gênants)
    srt_path_escaped = srt_path.replace("\\", "/").replace(":", "\\:")

    try:
        cmd = [
            "ffmpeg",
            "-i", "pipe:0",
            # Le filtre subtitles requiert un fichier physique dans la plupart des builds
            "-vf", f"subtitles='{srt_path_escaped}'", 
            "-f", "mp4",
            "-movflags", "frag_keyframe+empty_moov",
            "pipe:1"
        ]
        
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out_bytes, err = process.communicate(input=video_bytes)

        if process.returncode != 0:
            logging.error(f"Hard Merge Error: {err.decode()}")
            raise RuntimeError("Erreur incrustation vidéo.")
            
        return out_bytes

    finally:
        if os.path.exists(srt_path):
            os.remove(srt_path)
