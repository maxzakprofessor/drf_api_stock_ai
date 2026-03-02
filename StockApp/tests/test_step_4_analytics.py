import pytest
import logging
from django.urls import reverse
from rest_framework.test import APIClient
from StockApp.tests.factories import GoodsFactory, StocksFactory, UserFactory
from StockApp.models import Goodincomes, Goodmoves

logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestStep4Analytics:
    """Группа тестов: Складская аналитика и PDF (Шаг 4)"""

    def test_01_stock_balance_calculation(self):
        """ШАГ 4.1: Проверка математической формулы остатков"""
        # 1. Подготовка: Товар и два склада
        product = GoodsFactory(nameGood="Cement_M500")
        stock_a = StocksFactory(nameStock="Warehouse_A")
        stock_b = StocksFactory(nameStock="Shop_B")
        
        # 2. ОПЕРАЦИЯ 1: Приход 100 ед. на Склад А
        Goodincomes.objects.create(good=product, stock=stock_a, qty=100)
        logger.info(f"--- [SQL] Приход: 100 {product.nameGood} на {stock_a.nameStock} ---")

        # 3. ОПЕРАЦИЯ 2: Перемещение 40 ед. со Склада А на Склад Б
        Goodmoves.objects.create(good=product, stockFrom=stock_a, stockTo=stock_b, qty=40)
        logger.info(f"--- [SQL] Перемещение: 40 ед. из {stock_a.nameStock} в {stock_b.nameStock} ---")

        # 4. ЗАПРОС К API: Получаем остатки
        client = APIClient()
        client.force_authenticate(user=UserFactory())
        url = reverse('goodrests', kwargs={'wnameStock': 'Все', 'wnameGood': 'Все'})
        response = client.get(url)

        # 5. ПРОВЕРКА МАТЕМАТИКИ
        balances = {item['nameStock']: item['qty'] for item in response.data}
        
        logger.warning(f"--- [ANALYTICS] Результат расчета: {balances} ---")
        
        assert balances["Warehouse_A"] == 60  # 100 - 40
        assert balances["Shop_B"] == 40       # 0 + 40
        logger.info("✅ Формула остатков (Приход - Уход + Приход) верна!")

    def test_02_pdf_generation_endpoint(self):
        """ШАГ 4.2: Проверка генерации PDF-файла"""
        # Создаем минимальные данные для отчета
        Goodincomes.objects.create(good=GoodsFactory(), stock=StocksFactory(), qty=10)
        
        client = APIClient()
        client.force_authenticate(user=UserFactory())
        
        # POST запрос на тот же URL генерирует PDF (согласно твоему views.py)
        url = reverse('goodrests', kwargs={'wnameStock': 'Все', 'wnameGood': 'Все'})
        response = client.post(url)
        
        logger.info(f"--- [PDF] Запрос на генерацию отчета. Status: {response.status_code} ---")
        
        # ПРОВЕРКИ:
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
        # Проверяем, что в теле ответа есть данные (файл не пустой)
        assert len(response.getvalue()) > 0
        logger.info(f"--- [PDF] Файл успешно сформирован. Размер: {len(response.getvalue())} байт ---")
