from django.contrib import admin
from .models import Goods, Stocks, Goodincomes, Goodmoves, Tenant, UserProfile

# 1. Настройка отображения КОМПАНИЙ (Tenants)
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'is_active')
    search_fields = ('name',)

# 2. Настройка ПРОФИЛЕЙ (Связь Юзер <-> Компания)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant')
    list_filter = ('tenant',)

# 3. Настройка СКЛАДОВ (Теперь с фильтром по компании)
@admin.register(Stocks)
class StocksAdmin(admin.ModelAdmin):
    list_display = ('nameStock', 'tenant') # Видим компанию сразу в списке
    list_filter = ('tenant',)              # Можем фильтровать склады по компаниям
    search_fields = ('nameStock',)

# 4. Настройка ТОВАРОВ
@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ('nameGood', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('nameGood',)

# Прямая регистрация для журналов (можно тоже донастроить позже)
admin.site.register(Goodincomes)
admin.site.register(Goodmoves)

# Красивый заголовок для админки
admin.site.site_header = "Sklad PRO SaaS - Панель Управления"
admin.site.index_title = "Управление Multi-tenant инфраструктурой"
