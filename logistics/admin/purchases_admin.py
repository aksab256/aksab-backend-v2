# logistics/admin/purchases_admin.py
from django.contrib import admin
from ..models.purchases import Supplier, PurchaseInvoice, PurchaseItem

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    # عطلنا autocomplete حالياً عشان نضمن لقط الباركود في القائمة العادية
    # autocomplete_fields = ['product'] 
    fields = ('product', 'quantity_in_main_unit', 'cost_price_per_main_unit')

@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'supplier', 'warehouse', 'date', 'total_amount')
    readonly_fields = ('total_amount',)
    inlines = [PurchaseItemInline]

    # الجزء المطور لحقن السكربتات
    class Media:
        js = (
            # الرابط المباشر للمكتبة لضمان استقرار التشغيل
            'https://unpkg.com/html5-qrcode/html5-qrcode.min.js',
            # ملف السكربت بتاعك (تأكد من تحديثه بالكود اللي بعتهولك سابقاً)
            'js/admin_barcode_scanner.js',
        )

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'balance')
    search_fields = ('name',)

