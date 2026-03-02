from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    GoodViewSet, StockViewSet, GoodIncomeViewSet, GoodMoveViewSet, 
    GoodSaleViewSet, # <--- НОВЫЙ ИМПОРТ
    GoodRestView, MyTokenObtainPairView, AIAnalyzeView,
    UserAdminView, UpdatePasswordView, DashboardStatsView,
    RegisterRequestView, RegisterConfirmView
)

# 1. НАСТРОЙКА РОУТЕРА
router = DefaultRouter()
router.register(r'goods', GoodViewSet, basename='goods')
router.register(r'stocks', StockViewSet, basename='stocks')
router.register(r'goodincomes', GoodIncomeViewSet, basename='goodincomes')
router.register(r'goodmoves', GoodMoveViewSet, basename='goodmoves')
# РЕГИСТРИРУЕМ ПРОДАЖИ (Расход)
router.register(r'goodsales', GoodSaleViewSet, basename='goodsales')

# 2. СПИСОК МАРШРУТОВ (URLS)
urlpatterns = [
    # SAAS РЕГИСТРАЦИЯ
    path('register/request/', RegisterRequestView.as_view(), name='reg-request'),
    path('register/confirm/', RegisterConfirmView.as_view(), name='reg-confirm'),

    # АВТОРИЗАЦИЯ
    path('auth/signin', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/update-password', UpdatePasswordView.as_view(), name='update_password'),

    # УПРАВЛЕНИЕ ПЕРСОНАЛОМ
    path('auth/admin/all-users', UserAdminView.as_view(), name='all_users'),
    path('auth/admin/create-user', UserAdminView.as_view(), name='create_user'),
    path('auth/admin/delete-user/<int:pk>/', UserAdminView.as_view(), name='delete_user'),

    # АНАЛИТИКА И AI
    path('goodrests/<str:wnameStock>/<str:wnameGood>/', GoodRestView.as_view(), name='goodrests'),
    path('ai-analyze/', AIAnalyzeView.as_view(), name='ai_analyze'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),

    # CRUD ОПЕРАЦИИ (Goods, Stocks, Incomes, Moves, Sales)
    path('', include(router.urls)),
]
