from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Goods, Stocks, Goodincomes, Goodmoves

# 1. КАСТОМНЫЙ ВХОД (JWT)
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Вызываем базовую проверку логина и пароля
        data = super().validate(attrs)
        
        # КЛЮЧЕВОЙ МОМЕНТ: Если пользователь еще ни разу не входил (last_login is None),
        # мы отправляем True. Как только он сменит пароль, это поле станет False.
        data['needsPasswordChange'] = self.user.last_login is None
        
        # Передаем имя пользователя для отображения в интерфейсе Vue
        data['username'] = self.user.username
        return data

# 2. БАЗОВЫЕ СЕРИАЛИЗАТОРЫ (Справочники)
class GoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stocks
        fields = '__all__'

# 3. СЕРИАЛИЗАТОР ПРИХОДОВ
class GoodcomineSerializer(serializers.ModelSerializer):
    # Достаем текстовые названия из связанных таблиц
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
