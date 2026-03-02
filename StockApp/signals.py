import pymongo
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
# Импортируем все три модели для полного контроля склада
from .models import Goods, Goodincomes, Goodmoves 

from .session_context import identity

# 1. Подключение к NoSQL "Архиву"
client = pymongo.MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]
audit_collection = db['audit_logs']

# Универсальный помощник для записи в MongoDB

def save_to_nosql(event_type, instance, details):
    # Берем имя, которое мы зафиксировали при входе
    user_name = identity.get_user()

    log_entry = {
        "event": event_type,
        "timestamp": datetime.now().isoformat(),
        "user": user_name, # Всегда будет admin или тот, кто вошел
        "details": details
    }
    audit_collection.insert_one(log_entry)


# --- СЛУШАТЕЛИ СОБЫТИЙ (SIGNALS) ---

# 2. Логируем создание НОВОГО ТОВАРА (Goods)
@receiver(post_save, sender=Goods)
def log_new_good(sender, instance, created, **kwargs):
    if created:
        details = {
            "name": instance.nameGood,
            "action": "Initial registration of item"
        }
        save_to_nosql("CREATE_GOOD", instance, details)

# 3. Логируем ПРИХОД товара (Goodincomes)
@receiver(post_save, sender=Goodincomes)
def log_income(sender, instance, created, **kwargs):
    if created:
        details = {
            "good": instance.good.nameGood,
            "stock": instance.stock.nameStock,
            "quantity": instance.qty,
            "operation": "External Income"
        }
        save_to_nosql("INVENTORY_ADD", instance, details)

# 4. Логируем ПЕРЕМЕЩЕНИЕ товара (Goodmoves)
@receiver(post_save, sender=Goodmoves)
def log_move(sender, instance, created, **kwargs):
    if created:
        details = {
            "good": instance.good.nameGood,
            "from_stock": instance.stockFrom.nameStock,
            "to_stock": instance.stockTo.nameStock,
            "quantity": instance.qty,
            "operation": "Inter-warehouse Transfer"
        }
        save_to_nosql("INVENTORY_MOVE", instance, details)


