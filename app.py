from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import socketio
import asyncio
from socket_manager import SocketManager

# Pydantic model for the request body
class BroadcastMessage(BaseModel):
    message: str

# Socket.IO setup
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_manager = SocketManager(sio)

app = FastAPI()
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Registering Socket.IO events
@sio.event
async def connect(sid, environ):
    await socket_manager.on_connect(sid, environ)

@sio.event
async def disconnect(sid):
    await socket_manager.on_disconnect(sid)

# FastAPI HTTP endpoint to broadcast data
@app.post("/broadcast/")
async def broadcast_data(data: BroadcastMessage):
    message = data.message
    if not message:
        raise HTTPException(status_code=400, detail="No message provided")
    await socket_manager.broadcast_message(message)
    return {"detail": "Message has been broad casted "}

# FastAPI startup event
@app.on_event("startup")
async def startup_event():
    await asyncio.sleep(5)
    await socket_manager.broadcast_message("How are you?")

# Mount the Socket.IO app
app.mount("/", socket_app)

# Run the app using Uvicorn if the script is the main program
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
