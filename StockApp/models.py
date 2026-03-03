from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# 0. Справочник КОМПАНИЙ (Tenants)
# Фундамент для SaaS: разделяет данные разных клиентов
class Tenant(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название компании")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# Расширяем стандартного пользователя Django, чтобы привязать его к Компании
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users')

    def __str__(self):
        return f"{self.user.username} ({self.tenant.name})"

# 1. Справочник ТОВАРОВ (ТМЦ)
# Теперь каждый товар принадлежит конкретной компании
class Goods(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='goods')
    nameGood = models.CharField(max_length=500)

    def __str__(self): 
        return self.nameGood

# 2. Справочник СКЛАДОВ
# Склад жестко привязан к компании
class Stocks(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='stocks')
    nameStock = models.CharField(max_length=500)

    def __str__(self): 
        return f"{self.nameStock} | {self.tenant.name}"

# 3. Журнал ПРИХОДОВ
class Goodincomes(models.Model):
    # Связи подтягивают tenant автоматически через stock и good
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    good = models.ForeignKey(Goods, on_delete=models.CASCADE)
    qty = models.IntegerField(default=0)
    datetime = models.DateTimeField(default=timezone.now)

    @property
    def nameStock(self): 
        return self.stock.nameStock

    @property
    def nameGood(self): 
        return self.good.nameGood

# 4. Журнал ПЕРЕМЕЩЕНИЙ
class Goodmoves(models.Model):
    stockFrom = models.ForeignKey(Stocks, on_delete=models.CASCADE, related_name='moves_from')
    stockTo = models.ForeignKey(Stocks, on_delete=models.CASCADE, related_name='moves_to')
    good = models.ForeignKey(Goods, on_delete=models.CASCADE)
    qty = models.IntegerField(default=0)
    datetime = models.DateTimeField(default=timezone.now)

    @property
    def nameStockFrom(self): 
        return self.stockFrom.nameStock

    @property
    def nameStockTowhere(self): 
        return self.stockTo.nameStock

    @property
    def nameGood(self): 
        return self.good.nameGood

import uuid
class RegistrationRequest(models.Model):
    """Временное хранилище заявок на регистрацию компании"""
    email = models.EmailField(unique=True)
    company_name = models.CharField(max_length=255)
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} -> {self.company_name}"

class Goodsales(models.Model):
    """Продажи / Расход со склада"""
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    good = models.ForeignKey(Goods, on_delete=models.CASCADE)
    qty = models.FloatField()
    price = models.FloatField(default=0.0) 
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale: {self.good.nameGood} ({self.qty}) from {self.stock.nameStock}"
