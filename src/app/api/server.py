import shutil
from pathlib import Path

from app.main import main  # ta fonction de transcription
from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent  
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Page d’upload
@app.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# Traitement de la vidéo
@app.post("/transcribe")
async def transcribe(file: UploadFile):

    input_folder = Path("video_input")
    input_folder.mkdir(exist_ok=True)

    # Chemin final
    input_path = input_folder / file.filename

    # Sauvegarde du fichier uploadé
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Appel à ta fonction principale
    transcription = main(file.filename)

    return {
        "message": "Transcription effectuée avec succès",
        "transcription": transcription,
        "input_file": file.filename
    }
