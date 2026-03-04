from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import Goods, Stocks, Goodincomes, Goodmoves
from ..serializers import GoodSerializer, StockSerializer, GoodcomineSerializer, GoodmoveSerializer
import sys

class MultiTenantViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_tenant(self):
        print("🔍 [DEBUG] Получаем профиль пользователя...", file=sys.stderr)
        if hasattr(self.request.user, 'profile'):
            tenant = self.request.user.profile.tenant
            print(f"✅ [DEBUG] Tenant найден: {tenant.name}", file=sys.stderr)
            return tenant
        print("⚠️ [DEBUG] Профиль не найден!", file=sys.stderr)
        return None

class GoodViewSet(MultiTenantViewSet):
    serializer_class = GoodSerializer

    def get_queryset(self):
        print("📥 [DEBUG] GET запрос на список товаров...", file=sys.stderr)
        qs = Goods.objects.all()
        print(f"📊 [DEBUG] Найдено товаров в базе: {qs.count()}", file=sys.stderr)
        return qs
    
    def perform_create(self, serializer):
        print("🚀 [DEBUG] Начинаем создание товара...", file=sys.stderr)
        tenant = self.get_tenant()
        
        print(f"📝 [DEBUG] Данные для сохранения: {self.request.data}", file=sys.stderr)
        
        try:
            print("💾 [DEBUG] Вызываем serializer.save()...", file=sys.stderr)
            serializer.save(tenant=tenant)
            print("✨ [DEBUG] ТОВАР УСПЕШНО СОХРАНЕН В POSTGRES!", file=sys.stderr)
        except Exception as e:
            print(f"❌ [DEBUG] ОШИБКА ПРИ СОХРАНЕНИИ: {str(e)}", file=sys.stderr)
            raise e

class StockViewSet(MultiTenantViewSet):
    serializer_class = StockSerializer
    def get_queryset(self):
        return Stocks.objects.filter(tenant=self.get_tenant())
    def perform_create(self, serializer):
        serializer.save(tenant=self.get_tenant())

class GoodIncomeViewSet(MultiTenantViewSet):
    serializer_class = GoodcomineSerializer
    def get_queryset(self):
        return Goodincomes.objects.all()

class GoodMoveViewSet(MultiTenantViewSet):
    serializer_class = GoodmoveSerializer
    def get_queryset(self):
        return Goodmoves.objects.all()
