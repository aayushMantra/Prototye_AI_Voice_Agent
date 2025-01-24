class VoiceRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        
        this.startButton = document.getElementById('startRecord');
        this.stopButton = document.getElementById('stopRecord');
        this.transcriptionDiv = document.getElementById('transcription');
        this.clearButton = document.getElementById('clearTranscription');
        this.statusContainer = document.querySelector('.status-container');
        
        this.initializeButtons();
    }

    initializeButtons() {
        this.startButton.addEventListener('click', () => this.startRecording());
        this.stopButton.addEventListener('click', () => this.stopRecording());
        this.clearButton.addEventListener('click', () => this.clearTranscription());
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = async () => {
                await this.processRecording();
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateUI(true);
            this.showStatus('Recording in progress...');

        } catch (error) {
            console.error('Error accessing microphone:', error);
            this.showStatus('Error accessing microphone. Please check permissions.', true);
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.updateUI(false);
            this.showStatus('Processing audio...');
        }
    }

    async processRecording() {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio_data', audioBlob);

        try {
            const response = await fetch('http://localhost:8000/audio/record-live', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.displayTranscription(result.transcription_text);
            this.showStatus('Transcription complete!');
        } catch (error) {
            console.error('Error processing audio:', error);
            this.showStatus('Error processing audio. Please try again.', true);
        }

        this.audioChunks = [];
    }

    displayTranscription(text) {
        const timestamp = new Date().toLocaleTimeString();
        this.transcriptionDiv.innerHTML = `
            <div class="transcription-content">
                <div class="transcription-header">
                    <h3>Transcription at ${timestamp}</h3>
                </div>
                <div class="transcription-text">
                    ${text}
                </div>
            </div>
        `;
    }

    clearTranscription() {
        this.transcriptionDiv.innerHTML = '<p class="placeholder">Your transcribed text will appear here...</p>';
        this.showStatus('Transcription cleared');
    }

    updateUI(isRecording) {
        this.startButton.disabled = isRecording;
        this.stopButton.disabled = !isRecording;
    }

    showStatus(message, isError = false) {
        const statusDiv = document.createElement('div');
        statusDiv.className = `status ${isError ? 'error' : ''}`;
        statusDiv.textContent = message;
        
        const existingStatus = this.statusContainer.querySelector('.status');
        if (existingStatus) {
            this.statusContainer.removeChild(existingStatus);
        }
        this.statusContainer.appendChild(statusDiv);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new VoiceRecorder();
});
