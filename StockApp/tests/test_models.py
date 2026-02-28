import pytest
from StockApp.tests.factories import GoodsFactory, StocksFactory

@pytest.mark.django_db
def test_models_creation():
    good = GoodsFactory(nameGood="Арматура")
    stock = StocksFactory(nameStock="Склад А")
    
    assert good.nameGood == "Арматура"
    assert stock.nameStock == "Склад А"
    print("\n✅ Базовый тест моделей пройден!")
