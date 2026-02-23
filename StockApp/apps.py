# Импортируем базовый класс для конфигурации приложений Django
from django.apps import AppConfig

# Основной класс настроек для вашего приложения склада
class StockappConfig(AppConfig):
    # Указываем тип поля для автоматически создаваемых ID (первичных ключей) в моделях.
    # BigAutoField создает 64-битные числа, что стандарт для современных версий Django.
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Системное имя приложения. Должно точно совпадать с названием папки.
    # Это имя мы указывали в INSTALLED_APPS в файле settings.py.
    name = 'StockApp'
    
    # Понятное название для админ-панели (опционально)
    verbose_name = 'Учёт склада и товаров'

 
    # --- ДОБАВЛЯЕМ ЭТО ---
    def ready(self):
        # Импортируем файл сигналов при запуске сервера
        import StockApp.signals 

