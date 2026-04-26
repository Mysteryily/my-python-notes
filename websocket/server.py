import asyncio
import json
import websockets

HOST = "localhost"
PORT = 8080


class CServer:
    def __init__(self):
        self._connected = False
        self._running = False
        self._server = None
        self._loop = None
        self._client_ws = None
        self._send_queue = None
        self._on_message = None

    def set_on_message(self, handler):
        self._on_message = handler

    def send(self, data: dict):
        if self._loop and self._running and self._send_queue:
            asyncio.run_coroutine_threadsafe(
                self._send_queue.put(data), self._loop
            )
            return True
        return False

    def start(self):
        self._running = True
        asyncio.run(self._serve())

    def stop(self):
        self._running = False

    async def _serve(self):
        self._loop = asyncio.get_running_loop()
        self._send_queue = asyncio.Queue()
        self._server = await websockets.serve(
            self._on_websocket_connected, HOST, PORT,
            reuse_address=True
        )
        self._connected = True
        print(f"Server listening on ws://{HOST}:{PORT}")
        send_task = asyncio.create_task(self._send_loop())
        try:
            while self._running:
                await asyncio.sleep(0.5)
        finally:
            send_task.cancel()
            try:
                await send_task
            except asyncio.CancelledError:
                pass
            self._server.close()
            await self._server.wait_closed()
            self._connected = False

    async def _send_loop(self):
        while True:
            data = await self._send_queue.get()
            if self._client_ws:
                try:
                    await self._client_ws.send(json.dumps(data))
                    print(f"Server sent: seq={data.get('seq')}, msg={data.get('message')}")
                except websockets.exceptions.ConnectionClosed:
                    self._client_ws = None

    async def _on_websocket_connected(self, websocket):
        self._client_ws = websocket
        print("Client connected")
        try:
            async for message in websocket:
                data = json.loads(message)
                print(f"Server received: seq={data.get('seq')}, payload={data.get('payload')}")
                if self._on_message:
                    response = self._on_message(data)
                    if response:
                        await websocket.send(json.dumps(response))
                        print(f"Server response: seq={response.get('seq')}, computed={response.get('computed')}")
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        finally:
            if self._client_ws:
                self._client_ws = None
