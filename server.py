import socketio
import aiohttp
import socket
import datetime
from aiohttp import web
from zoneinfo import ZoneInfo
import asyncio
from datetime import datetime


Host = "127.0.0.1"
Port = 65432

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

async def index(request):
    """Serve the client-side application."""
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def frame_received(sid,data):
    est = ZoneInfo("America/New_York")
    timestamp  = datetime.now(est).isoformat()
    frame_size = len(data)
    await sio.emit("frame_feedback",{
        "timestamp": timestamp,
        "frame_size": frame_size
    },room=sid)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)

async def listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((Host, Port))
    s.setblocking(False)
    loop = asyncio.get_event_loop()
    est = ZoneInfo("America/New_York")
    while True:
        data, addr = await loop.sock_recvfrom(s, 65535)
        timestamp = datetime.now(est).isoformat()
        frame_size = len(data)
        await sio.emit("frame_feedback",{
        "timestamp": timestamp,
        "frame_size": frame_size
    })

app.router.add_static('/static', 'static')
app.router.add_get('/', index)

def main():
    loop = asyncio.get_event_loop()
    loop.create_task(listener())
    web.run_app(app, host=Host, port=Port)
main()