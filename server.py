import socketio
import aiohttp
import socket
from aiohttp import web
from zoneinfo import ZoneInfo
import asyncio
from datetime import datetime

Host = "127.0.0.1"
UDP_Port = 65432
HTTP_Port =8080

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def frame_received(sid,data):
    est = ZoneInfo("America/New_York")
    timestamp  = int(datetime.now(est).timestamp())
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
    s.bind((Host, UDP_Port))
    s.setblocking(False)
    loop = asyncio.get_event_loop()
    while True:
        data, address = await loop.sock_recvfrom(s, 65535)
        est = ZoneInfo("America/New_York")
        timestamp  = int(datetime.now(est).timestamp())
        frame_size = len(data)
        await sio.emit("frame_feedback",{
        "timestamp": timestamp,
        "frame_size": frame_size
    })

def main():
    loop = asyncio.get_event_loop()
    loop.create_task(listener())
    web.run_app(app, host=Host, port=HTTP_Port)
main()