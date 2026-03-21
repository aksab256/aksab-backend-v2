from django.contrib import admin
from django.contrib.auth.models import User
from .sales_admin import CustomUserAdmin
from ..models.sales_rep import SalesRepresentative
from ..models.sales_manager import SalesManager
# from ..models.store import Store
# from .store_admin import StoreAdmin

# إلغاء التسجيل القديم وتسجيل الجديد المنظم
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
admin.site.register(SalesRepresentative)
admin.site.register(SalesManager)
# admin.site.register(Store, StoreAdmin)
from .inventory_admin import WarehouseAdmin, InventoryItemAdmin

