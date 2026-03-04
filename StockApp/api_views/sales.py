from .inventory import MultiTenantViewSet
from ..models import Goodsales
from ..serializers import GoodsaleSerializer

class GoodSaleViewSet(MultiTenantViewSet):
    serializer_class = GoodsaleSerializer
    def get_queryset(self):
        tenant = self.get_tenant()
        # Фильтруем продажи: только моей компании
        if tenant:
            return Goodsales.objects.filter(stock__tenant=tenant).select_related('stock', 'good')
        return Goodsales.objects.none()
    
    def perform_create(self, serializer):
        serializer.save()
