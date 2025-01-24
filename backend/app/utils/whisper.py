import whisper
from pathlib import Path

# Initialize Whisper model
model = whisper.load_model("small")

# Directories
UPLOAD_DIR = Path("backend/app/uploads")
TRANSCRIPTION_DIR = Path("backend/app/transcriptions")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPTION_DIR.mkdir(parents=True, exist_ok=True)

def transcribe_audio(file_path: Path) -> str:
    """
    Transcribes an audio file and saves the result.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file '{file_path}' not found.")

    # Perform transcription
    result = model.transcribe(str(file_path))
    transcription_text = result["text"]

    # Save transcription
    transcription_file_path = TRANSCRIPTION_DIR / f"{file_path.stem}.txt"
    with open(transcription_file_path, "w", encoding="utf-8") as f:
        f.write(transcription_text)

    return str(transcription_file_path)

def transcribe_live_audio(audio_bytes: bytes) -> str:
    """
    Transcribes live audio input and returns the result.
    """
    result = model.transcribe(audio_bytes)
    return result["text"]
