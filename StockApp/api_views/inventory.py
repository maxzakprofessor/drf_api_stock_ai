from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import Goods, Stocks, Goodincomes, Goodmoves
from ..serializers import GoodSerializer, StockSerializer, GoodcomineSerializer, GoodmoveSerializer

class MultiTenantViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get_tenant(self):
        # Получаем компанию текущего пользователя
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.tenant
        return None

class GoodViewSet(MultiTenantViewSet):
    serializer_class = GoodSerializer
    def get_queryset(self):
        tenant = self.get_tenant()
        # 🔥 ИЗОЛЯЦИЯ ТОВАРОВ: Только мои товары
        return Goods.objects.filter(tenant=tenant).select_related('tenant') if tenant else Goods.objects.none()
    
    def perform_create(self, serializer):
        # Привязываем товар к компании создателя
        serializer.save(tenant=self.get_tenant())

class StockViewSet(MultiTenantViewSet):
    serializer_class = StockSerializer
    def get_queryset(self):
        tenant = self.get_tenant()
        # ИЗОЛЯЦИЯ СКЛАДОВ
        return Stocks.objects.filter(tenant=tenant).select_related('tenant') if tenant else Stocks.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.get_tenant())

class GoodIncomeViewSet(MultiTenantViewSet):
    serializer_class = GoodcomineSerializer
    def get_queryset(self):
        tenant = self.get_tenant()
        # ИЗОЛЯЦИЯ ПРИХОДОВ (через склад компании)
        if tenant:
            return Goodincomes.objects.filter(stock__tenant=tenant).select_related('stock', 'good')
        return Goodincomes.objects.none()
    
    def perform_create(self, serializer):
        serializer.save()

class GoodMoveViewSet(MultiTenantViewSet):
    serializer_class = GoodmoveSerializer
    def get_queryset(self):
        tenant = self.get_tenant()
        # ИЗОЛЯЦИЯ ПЕРЕМЕЩЕНИЙ (через склад-отправитель компании)
        if tenant:
            return Goodmoves.objects.filter(stockFrom__tenant=tenant).select_related('stockFrom', 'stockTo', 'good')
        return Goodmoves.objects.none()
    
    def perform_create(self, serializer):
        serializer.save()
