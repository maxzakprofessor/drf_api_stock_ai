from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Goods, Stocks, Goodincomes, Goodmoves, Goodsales

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        if hasattr(self.user, 'profile'):
            data['tenantName'] = self.user.profile.tenant.name
            data['tenantId'] = self.user.profile.tenant.id
        return data

class GoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ['id', 'nameGood', 'tenant']
        # 🔥 Убираем валидаторы с nameGood, чтобы Django не сканировал базу зря
        extra_kwargs = {
            'tenant': {'read_only': True},
            'nameGood': {'validators': []} 
        }

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stocks
        fields = ['id', 'nameStock', 'tenant']
        extra_kwargs = {'tenant': {'read_only': True}}

class GoodcomineSerializer(serializers.ModelSerializer):
    nameStock = serializers.ReadOnlyField(source='stock.nameStock')
    nameGood = serializers.ReadOnlyField(source='good.nameGood')
    class Meta:
        model = Goodincomes
        fields = ['id', 'stock', 'good', 'nameStock', 'nameGood', 'qty', 'datetime']

class GoodmoveSerializer(serializers.ModelSerializer):
    nameStockFrom = serializers.ReadOnlyField(source='stockFrom.nameStock')
    nameStockTowhere = serializers.ReadOnlyField(source='stockTo.nameStock')
    nameGood = serializers.ReadOnlyField(source='good.nameGood')
    class Meta:
        model = Goodmoves
        fields = ['id', 'stockFrom', 'stockTo', 'good', 'nameStockFrom', 'nameStockTowhere', 'nameGood', 'qty', 'datetime']

class GoodsaleSerializer(serializers.ModelSerializer):
    nameStock = serializers.ReadOnlyField(source='stock.nameStock')
    nameGood = serializers.ReadOnlyField(source='good.nameGood')
    class Meta:
        model = Goodsales
        fields = ['id', 'stock', 'good', 'nameStock', 'nameGood', 'qty', 'price', 'datetime']
