import pytest
from StockApp.models import Goods, Stocks
from StockApp.tests.factories import GoodsFactory, StocksFactory

@pytest.mark.django_db
class TestModels:
    def test_create_good(self):
        """ШАГ 1: Проверка создания товара"""
        item = Goods.objects.create(nameGood="Test Item 1")
        assert item.nameGood == "Test Item 1"
        assert Goods.objects.count() == 1

    def test_factory_works(self):
        """ШАГ 1: Проверка работы фабрик (Factory Boy)"""
        stock = StocksFactory(nameStock="Almaty Center")
        assert stock.nameStock == "Almaty Center"
