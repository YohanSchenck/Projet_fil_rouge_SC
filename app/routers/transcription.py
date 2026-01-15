import tempfile
from pathlib import Path

from app.services._transcription import transcription
from fastapi import APIRouter, FastAPI, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

router = APIRouter()

templates = Jinja2Templates(directory="app/routers/templates")

# Page d’upload
@router.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# Traitement de la vidéo
@router.post("/transcribe", name="transcribe")
async def transcribe(
    file: UploadFile, 
    subtitle_embed: bool = Form(False)
):

    #input_folder = Path("video_input")
    #input_folder.mkdir(exist_ok=True)

    # Lire le contenu
    content = await file.read()

    # Stocker temporairement le fichier dans un fichier unique
    #with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
    #    tmp.write(content)
    #    tmp_path = Path(tmp.name)

    # Appel à ta fonction principale
    transcription_output = await transcription(content, embed=subtitle_embed)

    # Nettoyer le fichier tmp
    #tmp_path.unlink(missing_ok=True)
    #tmp_path.with_suffix(".wav").unlink(True)

    return {
        "message": "Transcription effectuée avec succès",
        "transcription": transcription_output,
        "input_file": file.filename
    }



