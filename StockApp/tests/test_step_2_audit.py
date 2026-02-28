import pytest
import logging
from unittest.mock import patch
from StockApp.tests.factories import GoodsFactory, StocksFactory
from StockApp.models import Goodmoves
from StockApp.session_context import identity

logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestStep2Audit:
    """Группа тестов: Автоматический аудит в NoSQL (Шаг 2)"""

    @patch('StockApp.signals.audit_collection.insert_one')
    def test_01_inventory_move_audit(self, mock_insert_one):
        """ШАГ 2.1: Проверка логирования ПЕРЕМЕЩЕНИЯ товара"""
        
        # 1. Имитируем вход конкретного пользователя (как это делает JWT во Vue/Angular)
        current_user = "Zakiryanov_Manager"
        identity.set_user(current_user)
        logger.info(f"--- [AUTH] В систему вошел: {current_user} ---")

        # 2. Подготавливаем данные
        product = GoodsFactory(nameGood="Apple iPhone 15")
        stock_from = StocksFactory(nameStock="Almaty_Main")
        stock_to = StocksFactory(nameStock="Astana_Shop")

        # 3. ДЕЙСТВИЕ: Создаем перемещение в Django (SQL)
        move = Goodmoves.objects.create(
            stockFrom=stock_from,
            stockTo=stock_to,
            good=product,
            qty=10
        )
        logger.info(f"--- [SQL] Запись о перемещении создана в Django ---")

        # 4. ПРОВЕРКА MOCK (MongoDB): Что улетело в сигнал?
        assert mock_insert_one.called
        
        # Извлекаем данные, которые сигнал подготовил для Mongo
        # call_args[0][0] - это первый аргумент метода insert_one (наш словарь лога)
        log_entry = mock_insert_one.call_args[0][0]
        
        logger.warning(f"--- [NOSQL LOG] СОБЫТИЕ: {log_entry['event']} ---")
        logger.warning(f"--- [NOSQL LOG] КТО СДЕЛАЛ: {log_entry['user']} ---")
        logger.warning(f"--- [NOSQL LOG] ОТКУДА: {log_entry['details']['from_stock']} ---")
        logger.warning(f"--- [NOSQL LOG] КУДА: {log_entry['details']['to_stock']} ---")

        # Проверяем точность данных
        assert log_entry['user'] == current_user
        assert log_entry['event'] == "INVENTORY_MOVE"
        assert log_entry['details']['quantity'] == 10
