from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import Goods, Stocks, Goodincomes, Goodmoves
from ..serializers import GoodSerializer, StockSerializer, GoodcomineSerializer, GoodmoveSerializer

class MultiTenantViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get_tenant(self):
        return self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None

class GoodViewSet(MultiTenantViewSet):
    serializer_class = GoodSerializer
    def get_queryset(self):
        # Оставляем "сквозной" просмотр (видят все)
        return Goods.objects.all().select_related('tenant')
    
    def perform_create(self, serializer):
        # 🔥 ФИКС ОШИБКИ 500: Принудительно назначаем компанию создателя
        # Теперь база Neon не будет ругаться на пустое поле tenant_id
        serializer.save(tenant=self.get_tenant())

class StockViewSet(MultiTenantViewSet):
    serializer_class = StockSerializer
    def get_queryset(self):
        tenant = self.get_tenant()
        return Stocks.objects.filter(tenant=tenant).select_related('tenant') if tenant else Stocks.objects.none()
    def perform_create(self, serializer):
        serializer.save(tenant=self.get_tenant())

class GoodIncomeViewSet(MultiTenantViewSet):
    serializer_class = GoodcomineSerializer
    def get_queryset(self):
        tenant = self.get_tenant()
        return Goodincomes.objects.filter(stock__tenant=tenant).select_related('stock', 'good') if tenant else Goodincomes.objects.none()
    def perform_create(self, serializer):
        serializer.save()

class GoodMoveViewSet(MultiTenantViewSet):
    serializer_class = GoodmoveSerializer
    def get_queryset(self):
        tenant = self.get_tenant()
        return Goodmoves.objects.filter(stockFrom__tenant=tenant).select_related('stockFrom', 'stockTo', 'good') if tenant else Goodmoves.objects.none()
    def perform_create(self, serializer):
        serializer.save()
