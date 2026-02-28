import pytest
import logging
from django.urls import reverse
from rest_framework.test import APIClient
from StockApp.tests.factories import UserFactory, StocksFactory

logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestStep3API:
    """Группа тестов: Безопасность API и JWT (Шаг 3)"""

    def test_01_jwt_login_logic(self):
        """ШАГ 3.1: Получение токена и проверка флага смены пароля"""
        # Создаем юзера, который еще НЕ входил (last_login=None)
        password = "secret_pass_123"
        user = UserFactory(username="zakiryanov", last_login=None)
        user.set_password(password)
        user.save()

        client = APIClient()
        url = reverse('token_obtain_pair') # /auth/signin
        
        response = client.post(url, {'username': user.username, 'password': password}, format='json')
        
        logger.info(f"--- [API AUTH] Попытка входа пользователя: {user.username} ---")
        
        assert response.status_code == 200
        assert 'access' in response.data
        # Проверяем твою кастомную логику из serializers.py
        assert response.data['needsPasswordChange'] is True
        logger.info(f"--- [API AUTH] Токен получен. Флаг needsPasswordChange: {response.data['needsPasswordChange']} ---")

    def test_02_anonymous_access_denied(self):
        """ШАГ 3.2: Проверка блокировки анонимного доступа"""
        client = APIClient()
        # Пытаемся получить список складов без токена
        url = reverse('stocks-list') 
        response = client.get(url)
        
        logger.warning(f"--- [SECURITY] Аноним стучится в /api/stocks/. Статус ответа: {response.status_code} ---")
        
        # Ожидаем 401 Unauthorized, так как в settings.py стоит IsAuthenticated
        assert response.status_code == 401
        logger.warning("--- [SECURITY] Доступ анониму запрещен. Система в безопасности! ---")

    def test_03_authorized_access_success(self):
        """ШАГ 3.3: Проверка доступа с валидным токеном"""
        user = UserFactory()
        StocksFactory(nameStock="Almaty_Hub")
        
        client = APIClient()
        # Имитируем авторизацию (force_authenticate заменяет ручную передачу токена в тестах)
        client.force_authenticate(user=user)
        
        url = reverse('stocks-list')
        response = client.get(url)
        
        logger.info(f"--- [API ACCESS] Авторизованный юзер '{user.username}' запрашивает склады ---")
        assert response.status_code == 200
        assert len(response.data) > 0
        assert response.data[0]['nameStock'] == "Almaty_Hub"
        logger.info(f"--- [API ACCESS] Данные получены успешно: {response.data[0]['nameStock']} ---")
