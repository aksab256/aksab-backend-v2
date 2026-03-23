from django.contrib import admin
from django.contrib.auth.models import User
from .sales_admin import CustomUserAdmin
from ..models.sales_rep import SalesRepresentative
from ..models.sales_manager import SalesManager

# استيراد ملفات الأدمن (الاستيراد هنا يشغل الـ @admin.register تلقائياً)
from .customer_admin import CustomerAdmin
from .inventory_admin import WarehouseAdmin, InventoryItemAdmin, ProductAdmin, CategoryAdmin, StockTransferAdmin
from .invoice_admin import InvoiceAdmin
from .purchases_admin import SupplierAdmin, PurchaseInvoiceAdmin
from .supplier_payment_admin import SupplierPaymentAdmin
from .sales_return_admin import SalesReturnAdmin
from .transactions_admin import CollectionAdmin

# إعادة تسجيل مستخدمي النظام بالصلاحيات الجديدة
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)

# تسجيل الموديلات البسيطة التي لم ننشئ لها ملفات مستقلة بعد
try:
    admin.site.register(SalesRepresentative)
    admin.site.register(SalesManager)
except admin.sites.AlreadyRegistered:
    pass

