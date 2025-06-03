class IntelligentVoiceAssistant {
  constructor() {
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.isRecording = false;
    this.websocket = null;

    this.startButton = document.getElementById("startRecord");
    this.stopButton = document.getElementById("stopRecord");
    this.clearButton = document.getElementById("clearChat");
    this.chatMessages = document.getElementById("chatMessages");
    this.statusContainer = document.querySelector(".status-container");

    this.initializeButtons();
    this.initializeWebSocket();
  }

  initializeButtons() {
    this.startButton.addEventListener("click", () => this.startRecording());
    this.stopButton.addEventListener("click", () => this.stopRecording());
    this.clearButton.addEventListener("click", () => this.clearChat());
  }

  initializeWebSocket() {
    const connectWebSocket = () => {
      this.websocket = new WebSocket("ws://localhost:8000/chat/ws");

      this.websocket.onmessage = (event) => {
        const response = JSON.parse(event.data);
        this.addMessage(response.text, "bot");
      };

      this.websocket.onclose = () => {
        setTimeout(connectWebSocket, 3000); // Reconnect after 3 seconds
      };

      this.websocket.onerror = (error) => {
        console.error("WebSocket Error:", error);
        this.showStatus("Connection error. Please refresh the page.", true);
      };
    };
    connectWebSocket();
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
      this.showStatus("Recording in progress...");
    } catch (error) {
      console.error("Error accessing microphone:", error);
      this.showStatus(
        "Error accessing microphone. Please check permissions.",
        true
      );
    }
  }

  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
      this.isRecording = false;
      this.updateUI(false);
      this.showStatus("Processing audio...");
    }
  }

  async processRecording() {
    const audioBlob = new Blob(this.audioChunks, { type: "audio/webm" });
    const formData = new FormData();
    formData.append("audio_data", audioBlob);

    try {
      const response = await fetch("http://localhost:8000/audio/record-live", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      this.addMessage(result.transcription_text, "user");

      // Send transcribed text to Rasa through WebSocket
      if (this.websocket.readyState === WebSocket.OPEN) {
        this.websocket.send(result.transcription_text);
      }

      this.showStatus("Processing complete!");
    } catch (error) {
      console.error("Error processing audio:", error);
      this.showStatus("Error processing audio. Please try again.", true);
    }

    this.audioChunks = [];
  }

  addMessage(text, type) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${type}-message`;

    const timestamp = new Date().toLocaleTimeString();
    messageDiv.innerHTML = `
            ${text}
            <div class="message-time">${timestamp}</div>
        `;

    this.chatMessages.appendChild(messageDiv);
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }

  clearChat() {
    while (this.chatMessages.firstChild) {
      this.chatMessages.removeChild(this.chatMessages.firstChild);
    }
    this.addMessage(
      "Hello! I'm your AI assistant. How can I help you schedule meetings today?",
      "bot"
    );
    this.showStatus("Chat cleared");
  }

  updateUI(isRecording) {
    this.startButton.disabled = isRecording;
    this.stopButton.disabled = !isRecording;
  }

  showStatus(message, isError = false) {
    const statusDiv = document.createElement("div");
    statusDiv.className = `status ${isError ? "error" : ""}`;
    statusDiv.textContent = message;

    const existingStatus = this.statusContainer.querySelector(".status");
    if (existingStatus) {
      this.statusContainer.removeChild(existingStatus);
    }
    this.statusContainer.appendChild(statusDiv);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new IntelligentVoiceAssistant();
});
