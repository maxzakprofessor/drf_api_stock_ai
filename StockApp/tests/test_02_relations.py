import pytest
from StockApp.models import Goodincomes
from StockApp.tests.factories import GoodsFactory, StocksFactory

@pytest.mark.django_db
class TestRelations:
    def test_income_cascade_delete(self):
        """ШАГ 1.5: Проверка удаления склада и его приходов"""
        stock = StocksFactory()
        Goodincomes.objects.create(good=GoodsFactory(), stock=stock, qty=10)
        assert Goodincomes.objects.count() == 1
        stock.delete()
        assert Goodincomes.objects.count() == 0
