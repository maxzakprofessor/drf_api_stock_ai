import pytest
from unittest.mock import patch
from StockApp.tests.factories import GoodsFactory, StocksFactory, UserFactory
from StockApp.models import Goodmoves

@pytest.mark.django_db
class TestUserAudit:

    @patch('StockApp.signals.audit_collection.insert_one')
    def test_audit_logs_correct_user(self, mock_insert_one):
        """
        ПРОВЕРКА ПО КОСТОЧКАМ: 
        1. Имитируем вход конкретного пользователя.
        2. Совершаем перемещение товара.
        3. Проверяем, что в логе MongoDB именно ЭТОТ пользователь.
        """
        from StockApp.session_context import identity
        
        # 1. Имитируем, что в систему вошел пользователь "Zakiryanov"
        test_user = "Zakiryanov"
        identity.set_user(test_user)
        
        # 2. Создаем данные для перемещения
        product = GoodsFactory(nameGood="Apple iPhone 15")
        stock_from = StocksFactory(nameStock="Almaty_Warehouse")
        stock_to = StocksFactory(nameStock="Astana_Shop")

        # 3. ДЕЙСТВИЕ: Регистрируем перемещение в Django (SQL)
        Goodmoves.objects.create(
            stockFrom=stock_from,
            stockTo=stock_to,
            good=product,
            qty=5
        )

        # 4. ПРОВЕРКА MOCK: Вызвался ли сигнал?
        assert mock_insert_one.called
        
        # 5. ПРОВЕРКА ДАННЫХ В ЛОГЕ:
        # Извлекаем первый позиционный аргумент вызова insert_one
        log_entry = mock_insert_one.call_args[0][0]
        
        print(f"\n--- AUDIT LOG CHECK ---")
        print(f"User in system: {test_user}")
        print(f"User in Mongo log: {log_entry['user']}")
        print(f"Event: {log_entry['event']}")

        # ГЛАВНЫЙ ASSERT: имена должны совпадать
        assert log_entry['user'] == test_user
        assert log_entry['event'] == "INVENTORY_MOVE"
        assert log_entry['details']['from_stock'] == "Almaty_Warehouse"
        
        print("✅ Тест аудита пользователя пройден успешно!")

@pytest.mark.django_db
def test_identity_singleton_cleanup():
    """Проверяем, что наш Singleton хранит данные"""
    from StockApp.session_context import identity
    identity.set_user("Admin_Alpha")
    assert identity.get_user() == "Admin_Alpha"
    print("✅ Singleton корректно хранит имя пользователя")
