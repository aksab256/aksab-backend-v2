from django.contrib import admin
from django.contrib.auth.models import User
from .sales_admin import CustomUserAdmin
from ..models.sales_rep import SalesRepresentative
from ..models.sales_manager import SalesManager

# استيراد ملفات الأدمن لتفعيل الـ @admin.register
from .customer_admin import CustomerAdmin
from .inventory_admin import WarehouseAdmin, InventoryItemAdmin, ProductAdmin, CategoryAdmin, StockTransferAdmin
from .invoice_admin import InvoiceAdmin
from .purchases_admin import SupplierAdmin, PurchaseInvoiceAdmin
from .supplier_payment_admin import SupplierPaymentAdmin
from .sales_return_admin import SalesReturnAdmin
from .transactions_admin import CollectionAdmin

# 🆕 استيراد ملف الأدمن الخاص بالخزينة والعهدة
from .treasury_admin import RepresentativeVaultAdmin, CollectionActionAdmin, CompanyTreasuryAdmin

# 🆕 استيراد ملف الأدمن الخاص بالمصاريف
from .expenses_admin import ExpenseCategoryAdmin, ExpenseAdmin

# إعادة تسجيل مستخدمي النظام بالصلاحيات الجديدة
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)

# ملاحظة: تم حذف التسجيل اليدوي لـ SalesRepresentative و SalesManager
# لأنهما مسجلان بالفعل بـ @admin.register داخل ملفات الـ admin الخاصة بهما

