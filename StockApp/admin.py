from django.contrib import admin
from .models import Goods, Stocks, Goodincomes, Goodmoves

# Регистрируем модели, чтобы они появились в интерфейсе
admin.site.register(Goods)
admin.site.register(Stocks)
admin.site.register(Goodincomes)
admin.site.register(Goodmoves)
