# Импортируем стандартный модуль админки Django
from django.contrib import admin
# Импортируем path для создания путей и include для подключения маршрутов других приложений
from django.urls import path, include 

# ГЛАВНЫЙ СПИСОК МАРШРУТОВ ВСЕГО ПРОЕКТА
urlpatterns = [
    # Путь для входа в панель администратора (http://127.0.0.1)
    path('admin/', admin.site.urls),

    # ПОДКЛЮЧЕНИЕ ВАШЕГО ПРИЛОЖЕНИЯ StockApp
    # МЫ ГОВОРИМ DJANGO: "Все запросы, которые начинаются на api/, 
    # перенаправь в файл StockApp.urls для дальнейшей обработки"
    # Теперь ваши товары будут доступны по адресу: http://127.0.0.1
    path('api/', include('StockApp.urls')),
]
