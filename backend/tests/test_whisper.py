from backend.app.utils.whisper import transcribe_audio

if __name__ == "__main__":
    # Replace 'sample.wav' with your audio file name
    audio_file = "Perfect-(Mr-Jat.in).mp3"
    try:
        transcription_path = transcribe_audio(audio_file)
        print(f"Transcription completed! File saved at: {transcription_path}")
    except Exception as e:
        print(f"Error: {e}")

