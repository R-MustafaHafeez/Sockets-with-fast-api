import socketio

class SocketManager:
    def __init__(self, sio: socketio.AsyncServer):
        self.sio = sio
        self.connected_clients = {}

    async def send_message_to_client(self, sid, message):
        await self.sio.emit('message', {'data': message}, to=sid)

    async def broadcast_message(self, message):
        for sid in self.connected_clients:
            await self.send_message_to_client(sid, message)

    async def on_connect(self, sid, environ):
        print('Client connected', sid)
        self.connected_clients[sid] = True
        await self.send_message_to_client(sid, 'Welcome!')

    async def on_disconnect(self, sid):
        print('Client disconnected', sid)
        self.connected_clients.pop(sid, None)
