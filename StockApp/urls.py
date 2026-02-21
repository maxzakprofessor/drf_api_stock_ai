# Импортируем функцию path для создания маршрутов и include для подключения роутера
from django.urls import path, include
# Импортируем DefaultRouter — он автоматически создает стандартные пути (GET, POST, PUT, DELETE)
from rest_framework.routers import DefaultRouter
# Импортируем все наши логические блоки (классы) из файла views.py
from .views import (
    GoodViewSet, 
    StockViewSet, 
    GoodIncomeViewSet, 
    GoodMoveViewSet, 
    GoodRestView, 
    MyTokenObtainPairView,    
    AIAnalyzeView,
    UserAdminView,
    UpdatePasswordView,
    DashboardStatsView
)
# Импортируем стандартное вью для обновления JWT-токена (чтобы сессия не протухала)
from rest_framework_simplejwt.views import TokenRefreshView

# 1. НАСТРОЙКА РОУТЕРА
# Роутер берет ViewSet и сам делает пути:
# Например: /goods/ (список), /goods/1/ (один товар)
router = DefaultRouter()
router.register(r'goods', GoodViewSet, basename='goods')
router.register(r'stocks', StockViewSet, basename='stocks')
router.register(r'goodincomes', GoodIncomeViewSet, basename='goodincomes')
router.register(r'goodmoves', GoodMoveViewSet, basename='goodmoves')

# 2. СПИСОК МАРШРУТОВ (URLS)
urlpatterns = [
    # Подключаем все стандартные пути из роутера (товары, склады, приходы, перемещения)
    path('', include(router.urls)),

    # ПУТИ ДЛЯ АВТОРИЗАЦИИ
    # Вход в систему: Vue отправляет логин/пароль сюда
    path('auth/signin', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Обновление токена доступа (Access Token)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ПУТИ ДЛЯ ОТЧЕТОВ
    # Расчет остатков. <str:wnameStock> — это переменная (название склада), которая попадет во View.
    # Пример: /goodrests/Главный/Все/
    path('goodrests/<str:wnameStock>/<str:wnameGood>/', GoodRestView.as_view(), name='goodrests'),

    # Эндпоинт для работы с искусственным интеллектом (AI Анализ во Vue)
    path('ai-analyze/', AIAnalyzeView.as_view(), name='ai_analyze'),
        # Эндпоинты для управления персоналом (вызываются из UsersComponent.vue)
    path('auth/admin/all-users', UserAdminView.as_view(), name='all_users'),
    path('auth/admin/create-user', UserAdminView.as_view(), name='create_user'),
    path('auth/update-password', UpdatePasswordView.as_view(), name='update_password'),

    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
]
