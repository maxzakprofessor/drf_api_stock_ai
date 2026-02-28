import pytest
import logging
from unittest.mock import patch
from StockApp.tests.factories import GoodsFactory

logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestStep2Signals:
    @patch('StockApp.signals.audit_collection.insert_one')
    @patch('StockApp.signals.identity.get_user')
    def test_01_mongo_logging(self, mock_get_user, mock_insert_one):
        """ШАГ 2.1: Проверка лога в Mock MongoDB"""
        mock_get_user.return_value = "Admin_Zakiryanov"
        product = GoodsFactory(nameGood="AI_Sensor_v1")

        # Извлекаем данные из Mock-вызова
        log_data = mock_insert_one.call_args[0][0]
        
        logger.warning(f"--- [NOSQL LOG] Событие: {log_data['event']} ---")
        logger.warning(f"--- [NOSQL LOG] Пользователь: {log_data['user']} ---")
        logger.warning(f"--- [NOSQL LOG] Товар: {log_data['details']['name']} ---")
        
        assert log_data['user'] == "Admin_Zakiryanov"
