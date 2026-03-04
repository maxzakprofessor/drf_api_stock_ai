from django.apps import AppConfig
from django.conf import settings

class StockappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'StockApp'
    verbose_name = 'Учёт склада и товаров'

    def ready(self):
        # 🔥 УМНЫЙ РУБИЛЬНИК:
        # Если DEBUG=True (локально), подключаем сигналы и Mongo.
        # Если DEBUG=False (на Koyeb), пропускаем, чтобы не было тормозов 30с.
        if settings.DEBUG:
            try:
                import StockApp.signals
                print("🛠️ [DEBUG] Сигналы и MongoDB подключены локально.")
            except ImportError:
                print("⚠️ [DEBUG] Ошибка импорта сигналов.")
        else:
            # В облаке (Koyeb) эта часть кода даже не запустится! 🏎️💨
            print("🚀 [PROD] Сигналы (Mongo/Email) отключены для скорости API.")
