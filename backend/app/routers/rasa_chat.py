from fastapi import APIRouter, WebSocket, HTTPException
from starlette.websockets import WebSocketDisconnect
from typing import Dict, Any
import httpx
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["Chat"])

# Rasa server configuration
RASA_API_URL = "http://localhost:5005"


class ChatMessage(BaseModel):
    text: str
    sender: str = "user"


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            while True:
                message = await websocket.receive_text()

                try:
                    response = await client.post(
                        f"{RASA_API_URL}/webhooks/rest/webhook",
                        json={"message": message},
                        timeout=10.0,
                    )

                    if response.status_code != 200:
                        await websocket.send_json(
                            {
                                "text": "I'm experiencing technical difficulties. Please try again.",
                                "type": "error",
                            }
                        )
                        continue

                    rasa_response = response.json()

                    if not rasa_response:
                        await websocket.send_json(
                            {
                                "text": "I didn't catch that. Could you please rephrase?",
                                "type": "bot",
                            }
                        )
                        continue

                    for msg in rasa_response:
                        await websocket.send_json(
                            {
                                "text": msg.get("text", ""),
                                "type": "bot",
                                "metadata": msg.get("metadata", {}),
                            }
                        )

                except httpx.TimeoutException:
                    await websocket.send_json(
                        {
                            "text": "The request timed out. Please try again.",
                            "type": "error",
                        }
                    )
                except httpx.RequestError:
                    await websocket.send_json(
                        {
                            "text": "Unable to reach the bot service. Please try again later.",
                            "type": "error",
                        }
                    )

        except WebSocketDisconnect:
            print("Client disconnected")
        except Exception as e:
            print(f"WebSocket Error: {str(e)}")


@router.post("/message")
async def send_message(message: ChatMessage):
    """HTTP endpoint for sending messages to Rasa"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{RASA_API_URL}/webhooks/rest/webhook",
                json={"message": message.text, "sender": message.sender},
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=500, detail="Unable to process request at the moment"
                )

            rasa_response = response.json()
            return {
                "responses": [
                    {
                        "text": msg.get("text", ""),
                        "metadata": msg.get("metadata", {}),
                        "type": "bot",
                    }
                    for msg in rasa_response
                ]
            }

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503, detail="Service temporarily unavailable"
            )


@router.get("/health")
async def chat_health_check():
    """Check if Rasa server is accessible"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{RASA_API_URL}/version")
            if response.status_code == 200:
                version_info = response.json()
                return {
                    "status": "healthy",
                    "rasa_status": "connected",
                    "version": version_info.get("version", "unknown"),
                }
            return {"status": "unhealthy", "rasa_status": "disconnected"}
        except httpx.RequestError:
            return {"status": "unhealthy", "rasa_status": "unreachable"}
