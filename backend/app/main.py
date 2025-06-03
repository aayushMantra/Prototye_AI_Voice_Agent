from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import audio, rasa_chat

app = FastAPI(title="AI Voice Agent Prototype")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all@ origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="Frontend/static"), name="static")

# Include routes
app.include_router(audio.router)
app.include_router(rasa_chat.router)

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serve the Frontend HTML page"""
    return FileResponse("Frontend/index.html")

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "AI Voice Agent is running"}

