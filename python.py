import socketio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

# Socket.IO setup
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Dictionary to track connected clients
connected_clients = {}

# Pydantic model for the request body
class BroadcastMessage(BaseModel):
    message: str

# Function to send a message to a specific client
async def send_message_to_client(sid, message):
    await sio.emit('message', {'data': message}, to=sid)

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    print('Client connected', sid)
    connected_clients[sid] = True
    await send_message_to_client(sid, 'Welcome!')

@sio.event
async def disconnect(sid):
    print('Client disconnected', sid)
    connected_clients.pop(sid, None)

# Function to send a message to all connected clients
async def broadcast_message(message):
    for sid in connected_clients:
        await send_message_to_client(sid, message)

# FastAPI HTTP endpoint to broadcast data
@app.post("/broadcast/")
async def broadcast_data(data: BroadcastMessage):
    message = data.message
    if not message:
        raise HTTPException(status_code=400, detail="No message provided")
    await broadcast_message(message)
    return {"detail": "Message broadcasted"}

# FastAPI startup event
@app.on_event("startup")
async def startup_event():
    await asyncio.sleep(5)  # Wait for clients to connect
    await broadcast_message("How are you?")

# Mount the Socket.IO app
app.mount("/", socket_app)

# Run the app using Uvicorn if the script is the main program
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
