# logistics/admin/purchases_admin.py
from django.contrib import admin
from ..models.purchases import Supplier, PurchaseInvoice, PurchaseItem

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    fields = ('product', 'selected_unit', 'quantity', 'cost_price', 'line_total')
    readonly_fields = ('line_total',)
    autocomplete_fields = ['product']

@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'supplier', 'warehouse', 'date', 'total_amount')
    list_filter = ('supplier', 'warehouse', 'date')
    search_fields = ('invoice_no', 'supplier__name')
    readonly_fields = ('invoice_no', 'total_amount')
    inlines = [PurchaseItemInline]

    class Media:
        js = (
            'https://unpkg.com/html5-qrcode/html5-qrcode.min.js',
            'js/admin_barcode_scanner.js',
        )

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'balance')
    search_fields = ('name', 'phone')

