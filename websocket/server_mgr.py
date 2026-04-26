try:
    from .server import CServer
    from .singleton import ISingleton
except ImportError:
    from server import CServer
    from singleton import ISingleton


class CServerMgr(ISingleton):
    def __init__(self):
        super().__init__("CServerMgr")
        self._server = None
        self._on_message_handler = None

    def init_server(self):
        if self._server is None:
            self._server = CServer()
            if self._on_message_handler:
                self._server.set_on_message(self._on_message_handler)

    def set_on_message(self, handler):
        self._on_message_handler = handler
        if self._server:
            self._server.set_on_message(handler)

    def send(self, data: dict):
        if self._server:
            return self._server.send(data)
        return False

    def start(self):
        self.init_server()
        self._server.start()

    def stop(self):
        if self._server:
            self._server.stop()
