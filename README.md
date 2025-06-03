# AI Voice Agent Prototype

A sophisticated voice-based AI assistant that can process natural language, respond to voice commands, and perform various tasks through a conversational interface.

## Overview

This project implements a voice agent with the following capabilities:
- Real-time speech recognition
- Natural language understanding
- Voice response generation
- Interactive web interface

## Features

- **Voice Recognition**: Captures and transcribes user speech in real-time
- **Conversational AI**: Processes natural language to understand user intent
- **Voice Response**: Generates and speaks responses using text-to-speech
- **Web Interface**: Clean, responsive UI for interacting with the voice agent
- **Session Management**: Maintains context throughout conversations

## Project Structure

```
AI-Voice-Agent-Prototype/
├── Frontend/                  # Web interface
│   ├── index.html             # Main HTML page
│   └── static/                # Static assets
│       ├── css/               # Stylesheets
│       ├── js/                # JavaScript files
│       └── particles.json     # UI particle effects configuration
│
├── backend/                   # Server-side code
│   ├── app/                   # FastAPI application
│   │   ├── main.py            # Main application entry point
│   │   ├── routers/           # API route definitions
│   │   ├── transcriptions/    # Stored speech transcriptions
│   │   └── uploads/           # Voice recording storage
│   │
│   └── rasa_project/          # NLU components (optional)
│
└── ScreenShots/               # Application screenshots
```

## Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python, FastAPI
- **Speech Processing**: Web Speech API, OpenAI Whisper
- **AI/NLP**: Large Language Models for natural language understanding
- **Text-to-Speech**: Web Speech API

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js (optional, for development)
- Modern web browser with microphone access

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aayushMantra/Prototye_AI_Voice_Agent.git
   cd Prototye_AI_Voice_Agent
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Create a `.env` file in the root directory
   - Add necessary API keys and configuration parameters

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   python -m app.main
   ```

2. Open the frontend in your browser:
   - Navigate to `http://localhost:8000` in your web browser
   - Allow microphone access when prompted

## Usage

1. Click the microphone button to start recording
2. Speak your query or command
3. The system will process your speech and respond both visually and audibly
4. Continue the conversation naturally

## Future Enhancements

- Multi-language support
- Integration with additional services and APIs
- Enhanced context awareness
- Voice customization options
- Mobile application version

## Acknowledgments

- OpenAI for language model capabilities
- FastAPI for the efficient backend framework
- Web Speech API for browser-based speech recognition

---

*Note: This is a prototype application and may require additional configuration for production use.*
