from fastapi.testclient import TestClient
from pathlib import Path
from fastapi import status
from backend.app.main import app

# Set up constants
UPLOAD_DIR = Path("backend/app/uploads")
TRANSCRIPTION_DIR = Path("backend/app/transcriptions")
VALID_AUDIO_FILE = "test_audio.mp3"
INVALID_AUDIO_FILE = "test_invalid.txt"
NON_EXISTENT_FILE = "non_existent.mp3"

# Create test client
client = TestClient(app)

def test_upload_audio_valid_file():
    """Test uploading a valid audio file."""
    file_content = b"fake_audio_content"
    response = client.post(
        "/audio/upload-audio",
        files={"file": (VALID_AUDIO_FILE, file_content, "audio/mpeg")},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == f"File '{VALID_AUDIO_FILE}' uploaded successfully!"
    assert (UPLOAD_DIR / VALID_AUDIO_FILE).exists()

def test_upload_audio_invalid_file_type():
    """Test uploading an unsupported file type."""
    file_content = b"fake_invalid_content"
    response = client.post(
        "/audio/upload-audio",
        files={"file": (INVALID_AUDIO_FILE, file_content, "text/plain")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid file type" in response.json()["detail"]

def test_upload_audio_no_file():
    """Test uploading without providing a file."""
    response = client.post("/audio/upload-audio", files={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY  # Updated to match actual response
    assert "field required" in response.json()["detail"][0]["msg"].lower()

def test_transcribe_audio_valid_file(monkeypatch):
    """Test transcription for a valid file."""
    # Ensure directories exist
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTION_DIR.mkdir(parents=True, exist_ok=True)
    
    # Mock the whisper model's transcribe function directly
    def mock_model_transcribe(audio_path):
        return {"text": "Mock transcription text."}
        
    monkeypatch.setattr(
        "backend.app.utils.whisper.model.transcribe", 
        mock_model_transcribe
    )

    # Create test file with minimal valid MP3 content
    test_file_path = UPLOAD_DIR / VALID_AUDIO_FILE
    test_file_path.write_bytes(bytes.fromhex('FFFB9064000200004000'))  # Minimal valid MP3 header
    
    response = client.post(f"/audio/transcribe/{VALID_AUDIO_FILE}")
    assert response.status_code == status.HTTP_200_OK
    assert "transcription_text" in response.json()
    assert response.json()["transcription_text"] == "Mock transcription text."

def test_transcribe_audio_non_existent_file():
    """Test transcription for a non-existent file."""
    response = client.post(f"/audio/transcribe/{NON_EXISTENT_FILE}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert f"File '{NON_EXISTENT_FILE}' not found" in response.json()["detail"]

def test_transcribe_audio_unexpected_error(monkeypatch):
    """Test transcription when an unexpected error occurs."""
    # Create test file
    (UPLOAD_DIR / VALID_AUDIO_FILE).write_bytes(b"test audio content")
    
    def mock_transcribe_audio(file_path: Path) -> str:  # Updated parameter type
        raise Exception("Unexpected error during transcription.")

    monkeypatch.setattr(
        "backend.app.utils.whisper.transcribe_audio", 
        mock_transcribe_audio
    )

    response = client.post(f"/audio/transcribe/{VALID_AUDIO_FILE}")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An error occurred during transcription" in response.json()["detail"]
    
def test_record_live_audio():
    """Test live audio recording and transcription."""
    # Create sample WebM audio content
    audio_content = b"fake_webm_audio_content"
    
    response = client.post(
        "/audio/record-live",
        files={"audio_data": ("test_live.webm", audio_content, "audio/webm")}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "transcription_text" in response.json()
    assert "Live audio transcribed successfully" in response.json()["message"]

def test_transcribe_live_audio():
    file_content = b"fake_audio_content"
    response = client.post(
        "/audio/transcribe-live",
        files={"file": ("live_test.mp3", file_content, "audio/mpeg")},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "transcription_text" in response.json()
    assert response.json()["message"] == "Live transcription completed successfully!"