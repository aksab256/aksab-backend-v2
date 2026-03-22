from django.contrib import admin
from django.contrib.auth.models import User
from .sales_admin import CustomUserAdmin
from ..models.sales_rep import SalesRepresentative
from ..models.sales_manager import SalesManager

# 🆕 استيراد الأدمن الجديد الخاص بالعملاء
from .customer_admin import CustomerAdmin
from ..models.customers import Customer

# استيراد أدمن المخازن
from .inventory_admin import WarehouseAdmin, InventoryItemAdmin

# إلغاء التسجيل القديم وتسجيل الجديد المنظم لليوزرز
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
admin.site.register(SalesRepresentative)
admin.site.register(SalesManager)

# 🆕 تسجيل موديول العملاء في لوحة التحكم
admin.site.register(Customer, CustomerAdmin)

# وأي موديلات تانية للمخازن (لو محتاج تسجلهم هنا)
# admin.site.register(Warehouse, WarehouseAdmin)

