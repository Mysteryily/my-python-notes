class ISingleton:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

    def __init__(self, name):
        if not hasattr(self, '_initialized'):
            self.name = name
            self._initialized = True

    @classmethod
    def get_instance(cls):
        if cls not in cls._instances:
            cls()
        return cls._instances[cls]
