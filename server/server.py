import socketio
import socket
from aiohttp import web
from zoneinfo import ZoneInfo
import asyncio
from datetime import datetime

#configurations
Host = "127.0.0.1"
UDP_Port = 65432
HTTP_Port = 8080

#initialize Socket.IO server and attach to aiohttp web app
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

@sio.event
def connect(sid, environ):
    print("connect", sid)

@sio.event
def disconnect(sid):
    print("disconnect", sid)

#listens for UDP packets and emits feedback
async def listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((Host, UDP_Port))
    s.setblocking(False)
    loop = asyncio.get_running_loop()
    while True:
        data, address = await loop.sock_recvfrom(s, 65535)
        est = ZoneInfo("America/New_York")
        timestamp = int(datetime.now(est).timestamp())
        frame_size = len(data)
        print("Received: " + str(frame_size) + " bytes from " + str(address))
        await sio.emit("frame_feedback", {
            "timestamp": timestamp,
            "frame_size": frame_size
        })

#runs aiohttp app and listener together
async def main():
    asyncio.create_task(listener())
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner,host=Host,port=HTTP_Port)
    await site.start()
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
