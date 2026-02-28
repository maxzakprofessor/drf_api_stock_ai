import factory
from StockApp.models import Goods, Stocks
from django.contrib.auth.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Faker('user_name')

class GoodsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Goods
    nameGood = factory.Faker('word')

class StocksFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Stocks
    nameStock = factory.Faker('city')
