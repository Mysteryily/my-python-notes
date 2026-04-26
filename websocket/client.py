import asyncio
import json
import threading
import websockets

SERVER_URI = "ws://localhost:8080"


class CClient:
    def __init__(self):
        self._uri = SERVER_URI
        self._connected = False
        self._running = False
        self._loop = None
        self._thread = None
        self._send_queue = None
        self._on_message = None

    def set_on_message(self, handler):
        self._on_message = handler

    def send(self, data: dict):
        if not self._loop or not self._connected:
            return False
        asyncio.run_coroutine_threadsafe(self._send_queue.put(data), self._loop)
        return True

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=7)

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._send_queue = asyncio.Queue()
        self._loop.create_task(self._reconnect_loop())
        try:
            self._loop.run_forever()
        finally:
            pending = asyncio.all_tasks(self._loop)
            for task in pending:
                task.cancel()
            self._loop.run_until_complete(
                asyncio.gather(*pending, return_exceptions=True)
            )
            self._loop.close()
            self._loop = None

    async def _reconnect_loop(self):
        while self._running:
            try:
                async with websockets.connect(self._uri) as ws:
                    self._connected = True
                    print(f"Client connected to {self._uri}")
                    await self._handle_connection(ws)
            except (ConnectionRefusedError, OSError,
                    websockets.exceptions.WebSocketException) as e:
                self._connected = False
                if self._running:
                    print(f"Client connection failed: {e}, retrying in 5s...")
                    await asyncio.sleep(5)
            finally:
                self._connected = False
        self._loop.stop()

    async def _handle_connection(self, ws):
        send_task = asyncio.create_task(self._send_loop(ws))
        recv_task = asyncio.create_task(self._receive_loop(ws))
        done, pending = await asyncio.wait(
            [send_task, recv_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, websockets.exceptions.ConnectionClosed):
                pass

    async def _send_loop(self, ws):
        try:
            while self._running and self._connected:
                data = await self._send_queue.get()
                await ws.send(json.dumps(data))
                print(f"Client sent: seq={data.get('seq')}, payload={data.get('payload')}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if not self._running:
                try:
                    await ws.close()
                except Exception as e:
                    pass

    async def _receive_loop(self, ws):
        try:
            async for message in ws:
                data = json.loads(message)
                print(f"Client received: status={data.get('status')}, seq={data.get('seq')}, computed={data.get('computed')}")
                if self._on_message:
                    self._on_message(data)
        except websockets.exceptions.ConnectionClosed:
            pass
