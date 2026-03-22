from django.contrib import admin
from ..models.purchases import Supplier, PurchaseInvoice, PurchaseItem

# جدول الأصناف داخل الفاتورة (Inline)
class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    # هنخلي السيستم يختار الصنف بالبحث عشان لو الأصناف كتير
    autocomplete_fields = ['product'] 
    fields = ('product', 'quantity_in_main_unit', 'cost_price_per_main_unit')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'balance')
    search_fields = ('name', 'phone')

@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'supplier', 'warehouse', 'date', 'total_amount')
    list_filter = ('supplier', 'warehouse', 'date')
    search_fields = ('invoice_no', 'supplier__name')
    inlines = [PurchaseItemInline]

    # لو عايز تشغل السكانر جوه الفاتورة (اختياري بس بيسهل الشغل جداً)
    class Media:
        js = (
            'https://unpkg.com/html5-qrcode',
            'js/admin_barcode_scanner.js', 
        )

