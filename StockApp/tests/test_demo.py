import pytest
from StockApp.tests.factories import GoodsFactory, StocksFactory

@pytest.mark.django_db
def test_factory_visual_demo():
    print("\n--- START FACTORY MAGIC ---")
    
    # Create 3 goods
    for i in range(3):
        g = GoodsFactory()
        print(f"Item {i+1}: {g.nameGood}")
    
    # Create 2 stocks
    for i in range(2):
        s = StocksFactory()
        print(f"Warehouse {i+1}: {s.nameStock}")
    
    from StockApp.models import Goods
    assert Goods.objects.count() == 3
    print("--- TEST FINISHED: DB WILL BE CLEARED ---")
