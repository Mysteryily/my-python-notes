try:
    from .client import CClient
    from .singleton import ISingleton
except ImportError:
    from client import CClient
    from singleton import ISingleton


class CClientMgr(ISingleton):
    def __init__(self):
        super().__init__("CClientMgr")
        self._client = None
        self._on_message_handler = None

    def init_client(self):
        if self._client is None:
            self._client = CClient()
            if self._on_message_handler:
                self._client.set_on_message(self._on_message_handler)

    def send(self, data: dict):
        if self._client:
            return self._client.send(data)
        return False

    def set_on_message(self, handler):
        self._on_message_handler = handler
        if self._client:
            self._client.set_on_message(handler)

    def start(self):
        self.init_client()
        self._client.start()

    def stop(self):
        if self._client:
            self._client.stop()
