from rest_framework import serializers
from .models import Goods, Stocks, Goodincomes, Goodmoves, Goodsales

class GoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ['id', 'nameGood', 'tenant']
        # Помечаем tenant как необязательный, чтобы не было задержки на валидацию
        extra_kwargs = {'tenant': {'required': False, 'allow_null': True}}

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

# ... (остальные сериализаторы оставляем без изменений)
