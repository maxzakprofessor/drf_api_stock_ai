import pytest
import logging
from StockApp.models import Goods, Stocks, Goodincomes
from StockApp.tests.factories import GoodsFactory, StocksFactory

logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestStep1Core:
    def test_01_create_good(self):
        """ШАГ 1.1: Создание товара в БД"""
        item = Goods.objects.create(nameGood="Brick M150")
        logger.info(f"--- [SQL] Создан товар: ID={item.id}, Name={item.nameGood} ---")
        assert item.nameGood == "Brick M150"

    def test_02_income_relation(self):
        """ШАГ 1.3: Проверка связей (ForeignKey)"""
        product = GoodsFactory(nameGood="Cement")
        warehouse = StocksFactory(nameStock="Main Base")
        income = Goodincomes.objects.create(good=product, stock=warehouse, qty=250)
        
        logger.info(f"--- [RELATION] В БД записано: {income.qty} ед. '{income.nameGood}' на склад '{income.nameStock}' ---")
        assert income.nameGood == "Cement"
