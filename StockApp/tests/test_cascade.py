import pytest
from StockApp.tests.factories import GoodsFactory, StocksFactory
from StockApp.models import Goodincomes

@pytest.mark.django_db
def test_cascade_delete_stock():
    """Проверка: удаление склада удаляет связанные приходы"""
    warehouse = StocksFactory(nameStock="Temporary Warehouse")
    product = GoodsFactory(nameGood="Bricks")
    
    # Создаем приход
    income = Goodincomes.objects.create(good=product, stock=warehouse, qty=1000)
    assert Goodincomes.objects.count() == 1
    
    # УДАЛЯЕМ СКЛАД
    warehouse.delete()
    
    # ПРОВЕРЯЕМ: приход должен удалиться автоматически (on_delete=models.CASCADE)
    assert Goodincomes.objects.count() == 0
    print("\n✅ CASCADE DELETE TEST PASSED")
