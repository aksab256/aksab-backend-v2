from django.contrib import admin
from django.contrib.auth.models import User
from .sales_admin import CustomUserAdmin
from ..models.sales_rep import SalesRepresentative
from ..models.sales_manager import SalesManager

# 🆕 بنعمل Import بس عشان الملف يتقرأ والـ Decorator يشتغل
from .customer_admin import CustomerAdmin
from ..models.customers import Customer

# استيراد أدمن المخازن
from .inventory_admin import WarehouseAdmin, InventoryItemAdmin

# إلغاء التسجيل القديم وتسجيل الجديد للمستخدمين
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
admin.site.register(SalesRepresentative)
admin.site.register(SalesManager)
from .invoice_admin import InvoiceAdmin
# ❌ امسح أو عطل السطر ده (هو ده سبب المشكلة):
# admin.site.register(Customer, CustomerAdmin) 

# أضف هذا السطر
from .transactions_admin import CollectionAdmin

