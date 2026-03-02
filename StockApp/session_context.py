class IdentityContext:
    _instance = None
    _user_name = "system_init"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IdentityContext, cls).__new__(cls)
        return cls._instance

    def set_user(self, name):
        self._user_name = name

    def get_user(self):
        return self._user_name

# Создаем один объект на всё приложение
identity = IdentityContext()
