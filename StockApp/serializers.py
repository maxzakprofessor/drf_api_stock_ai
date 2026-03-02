from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Goods, Stocks, Goodincomes, Goodmoves, Goodsales

# 1. КАСТОМНЫЙ ВХОД (JWT + TENANT INFO)
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Добавляем флаг смены пароля
        data['needsPasswordChange'] = self.user.last_login is None
        data['username'] = self.user.username
        
        # Передаем название компании во фронтенд (для заголовка в Angular/Vue)
        if hasattr(self.user, 'profile'):
            data['tenantName'] = self.user.profile.tenant.name
            data['tenantId'] = self.user.profile.tenant.id
            
        return data

# 2. БАЗОВЫЕ СЕРИАЛИЗАТОРЫ (Справочники)
class TenantRestrictedSerializer(serializers.ModelSerializer):
    """Базовый класс: скрывает поле tenant от ручного ввода, но сохраняет его"""
    class Meta:
        # tenant помечаем как read_only, чтобы фронтенд его не присылал
        extra_kwargs = {'tenant': {'read_only': True}}

class GoodSerializer(TenantRestrictedSerializer):
    class Meta(TenantRestrictedSerializer.Meta):
        model = Goods
        fields = ['id', 'nameGood', 'tenant']

class StockSerializer(TenantRestrictedSerializer):
    class Meta(TenantRestrictedSerializer.Meta):
        model = Stocks
        fields = ['id', 'nameStock', 'tenant']

# 3. СЕРИАЛИЗАТОР ПРИХОДОВ
class GoodcomineSerializer(serializers.ModelSerializer):
    nameStock = serializers.ReadOnlyField(source='stock.nameStock')
    nameGood = serializers.ReadOnlyField(source='good.nameGood')
    class Meta:
        model = Goodincomes
        fields = ['id', 'stock', 'good', 'nameStock', 'nameGood', 'qty', 'datetime']

# 4. СЕРИАЛИЗАТОР ПЕРЕМЕЩЕНИЙ
class GoodmoveSerializer(serializers.ModelSerializer):
    nameStockFrom = serializers.ReadOnlyField(source='stockFrom.nameStock')
    nameStockTowhere = serializers.ReadOnlyField(source='stockTo.nameStock')
    nameGood = serializers.ReadOnlyField(source='good.nameGood')
    class Meta:
        model = Goodmoves
        fields = ['id', 'stockFrom', 'stockTo', 'good', 'nameStockFrom', 'nameStockTowhere', 'nameGood', 'qty', 'datetime']

#5. СЕРИАЛИЗАТОР ДЛЯ ПРОДАЖИ
class GoodsaleSerializer(serializers.ModelSerializer):
    nameStock = serializers.ReadOnlyField(source='stock.nameStock')
    nameGood = serializers.ReadOnlyField(source='good.nameGood')
    
    class Meta:
        model = Goodsales
        fields = ['id', 'stock', 'good', 'nameStock', 'nameGood', 'qty', 'price', 'datetime']

