from pydantic import BaseModel

class AudioFileResponse(BaseModel):
    message: str
    file_path: str