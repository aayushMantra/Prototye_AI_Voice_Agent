from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
from ..utils.whisper import transcribe_audio, transcribe_live_audio
from pathlib import Path
from fastapi.responses import JSONResponse
import shutil 
import whisper

# Initialize Whisper model (using base model for CPU efficiency)
model = whisper.load_model("small")

router = APIRouter(
    prefix="/audio",
    tags=["Audio"]
)

# Directory to save uploaded files
UPLOAD_DIR = Path("backend/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  

# Maximum file size in bytes (e.g., 10MB)
MAX_FILE_SIZE = 20 * 1024 * 1024 

ALLOWED_FILE_TYPES = [
    "audio/wav", 
    "audio/mpeg",
    "audio/mp3",
    "audio/ogg",
    "audio/webm",
    "audio/webm;codecs=opus",
    "audio/x-wav",
    "audio/x-mpeg",
    "audio/mpeg3",
    "video/mpeg"
]

@router.post("/upload-audio", summary="Upload an audio file")
async def upload_audio(file:UploadFile = File(...)):
    """
    Endpoint to upload an audio file and save it to the uploads/ directory.
    """
    
    # Validate file presence
    if not file:
        raise HTTPException(
            status_code=400,
            detail="No file provided. Please upload an audio file."
        )
        
    # Validate File Type
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Supported formats are: WAV, MP3, MPEG, OGG, and WebM."
        )

    print(f"Received file content type: {file.content_type}")
    
    await file.seek(0) # Reset cursor to the start
    
    # Create File Path:
    file_path = UPLOAD_DIR / file.filename
    
    # Save the File
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"message": f"File '{file.filename}' uploaded successfully!", "file_path": str(file_path)}

@router.post("/transcribe/{file_name}", summary="Transcribe an uploaded audio file")
async def transcribe(file_name: str):
    """
    Endpoint to transcribe an audio file.
    """
    try:
        transcription_path = transcribe_audio(file_name)
        with open(transcription_path, "r", encoding="utf-8") as f:
            transcription_text = f.read()
        
        return {
            "message": f"Transcription completed for file '{file_name}'.",
            "transcription_path": transcription_path,
            "transcription_text": transcription_text
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"File '{file_name}' not found in the uploads directory. Please upload the file first."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during transcription: {str(e)}"
        )

@router.post("/record-live", summary="Record and transcribe live audio")
async def record_live_audio(audio_data: UploadFile = File(...)):
    """
    Endpoint to handle live audio recording and transcription.
    Accepts WebRTC audio stream and returns transcription.
    """
    if audio_data.content_type not in ["audio/webm", "audio/wav", "audio/ogg"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid audio format. Please use WebM, WAV, or OGG format."
        )

    # Create unique filename for the recording
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"live_recording_{timestamp}.webm"
    audio_path = UPLOAD_DIR / audio_filename

    # Save the audio file
    try:
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio_data.file, f)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save audio file: {str(e)}"
        )

    # Transcribe the audio
    try:
        transcription_path = transcribe_audio(audio_path)
        with open(transcription_path, "r", encoding="utf-8") as f:
            transcription_text = f.read()

        return {
            "message": "Live audio transcribed successfully",
            "transcription_text": transcription_text,
            "audio_file": audio_filename,
            "transcription_path": str(transcription_path)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )

