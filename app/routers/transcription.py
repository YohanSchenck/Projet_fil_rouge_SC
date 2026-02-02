import io
import traceback

from app.schemas.enums import ResponseType
# Import de notre nouveau service et des enums
from app.services._transcription import transcription_service
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

router = APIRouter()
templates = Jinja2Templates(directory="app/routers/templates")

@router.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@router.post("/transcribe", name="transcribe")
async def transcribe(
    file: UploadFile, 
    response_type: ResponseType = Form(...) # L'utilisateur choisit via le formulaire
):
    # 1. Validation basique
    if not file:
        raise HTTPException(status_code=400, detail="No file sent")

    filename = file.filename
    content_type = file.content_type
    
    # Détection Audio vs Vidéo
    is_audio = "audio" in content_type
    
    # 2. Lecture en mémoire (Attention à la RAM pour gros fichiers)
    # Pour un MVP c'est OK, pour la prod on pourrait streamer par chunks 
    # mais ffmpeg a besoin de seek souvent.
    file_bytes = await file.read() 
    
    try:
        # 3. Appel du service
        data, media_type, out_filename = await transcription_service(
            file_bytes=file_bytes,
            file_name=filename,
            response_type=response_type,
            is_audio_file=is_audio
        )

        # 4. Retour du résultat sous forme de fichier téléchargeable
        return StreamingResponse(
            io.BytesIO(data), 
            media_type=media_type, 
            headers={
                "Content-Disposition": f"attachment; filename={out_filename}",
                "Access-Control-Expose-Headers": "Content-Disposition" # Important pour le JS
            }
        )

    except Exception as e:
        # Log l'erreur ici
        #print(f"Error processing: {e}")
        #raise HTTPException(status_code=500, detail="Processing failed")
        print("--- STACKTRACE ERREUR ---")
        traceback.print_exc() # Cela affichera la ligne exacte qui plante
        raise HTTPException(status_code=500, detail=str(e))
