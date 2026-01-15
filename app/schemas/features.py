from fastapi import UploadFile
from pydantic import BaseModel


class Input(BaseModel):
    # TODO : update with your model inputs
    file: UploadFile
    subtitle_embed: bool
