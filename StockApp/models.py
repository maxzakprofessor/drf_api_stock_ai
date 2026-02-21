# Из основного пакета Django импортируем модуль models.
# Он содержит инструменты для создания таблиц в базе данных (SQL).
# Каждая модель (класс) здесь станет отдельной таблицей.
from django.db import models

# Из системных утилит Django импортируем модуль timezone.
# Он нужен для корректной работы с датой и временем с учетом 
# часового пояса (TIME_ZONE), указанного в настройках settings.py.
from django.utils import timezone

# 1. Справочник ТОВАРОВ (ТМЦ)
# Хранит только список названий товаров (например: "Яблоки", "Цемент")
class Goods(models.Model):
    # Поле для названия товара (максимум 500 символов)
    nameGood = models.CharField(max_length=500)

    # Метод __str__ определяет, как товар будет называться в админке Django
    def __str__(self): 
        return self.nameGood

# 2. Справочник СКЛАДОВ
# Хранит места хранения (например: "Склад №1", "Магазин")
class Stocks(models.Model):
    # Поле для названия склада
    nameStock = models.CharField(max_length=500)

    # Отображение названия склада в интерфейсе управления
    def __str__(self): 
        return self.nameStock


# 3. Журнал ПРИХОДОВ (Поступление товара извне)
# Фиксирует, какой товар пришел и на какой конкретно склад
class Goodincomes(models.Model):
    # ForeignKey — это связь со складом. 
    # on_delete=models.CASCADE означает: если удалить склад, удалятся и его приходы.
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    
    # Связь с таблицей товаров
    good = models.ForeignKey(Goods, on_delete=models.CASCADE)
    
    # Количество (целое число, по умолчанию 0)
    qty = models.IntegerField(default=0)
    
    # Дата и время операции. timezone.now ставит текущее время автоматически.
    datetime = models.DateTimeField(default=timezone.now)

    # @property — "виртуальные" поля. Они не создают колонки в базе,
    # но позволяют Vue.js сразу видеть текстовые названия вместо ID.
    @property
    def nameStock(self): 
        return self.stock.nameStock

    @property
    def nameGood(self): 
        return self.good.nameGood


# 4. Журнал ПЕРЕМЕЩЕНИЙ (Движение товара между вашими складами)
# Фиксирует передачу товара со склада А на склад Б
class Goodmoves(models.Model):
    # Склад-отправитель. 
    # related_name нужен, чтобы Django различал две связи с одной таблицей Stocks.
    stockFrom = models.ForeignKey(Stocks, on_delete=models.CASCADE, related_name='moves_from')
    
    # Склад-получатель
    stockTo = models.ForeignKey(Stocks, on_delete=models.CASCADE, related_name='moves_to')
    
    # Какой именно товар перемещаем
    good = models.ForeignKey(Goods, on_delete=models.CASCADE)
    
    # Количество перемещаемого товара
    qty = models.IntegerField(default=0)
    
    # Время совершения перемещения
    datetime = models.DateTimeField(default=timezone.now)

    # Свойство для получения имени склада-отправителя (используется во Vue)
    @property
    def nameStockFrom(self): 
        return self.stockFrom.nameStock

    # Свойство для получения имени склада-получателя
    @property
    def nameStockTowhere(self): 
        return self.stockTo.nameStock

    # Свойство для получения названия товара
    @property
    def nameGood(self): 
        return self.good.nameGood

