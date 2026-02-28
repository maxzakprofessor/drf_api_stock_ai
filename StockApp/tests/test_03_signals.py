import pytest
from unittest.mock import patch
from StockApp.tests.factories import GoodsFactory

@pytest.mark.django_db
class TestSignals:
    @patch('StockApp.signals.audit_collection.insert_one')
    @patch('StockApp.signals.identity.get_user')
    def test_mongo_signal_on_create(self, mock_get_user, mock_insert_one):
        """ШАГ 2: Проверка отправки лога в Mock MongoDB"""
        mock_get_user.return_value = "Zakiryanov"
        GoodsFactory(nameGood="AI Controller")
        assert mock_insert_one.called
        log_entry = mock_insert_one.call_args[0][0]
        assert log_entry['user'] == "Zakiryanov"
        assert log_entry['event'] == "CREATE_GOOD"
