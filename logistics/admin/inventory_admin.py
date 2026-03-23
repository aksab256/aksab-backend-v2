from django.contrib import admin
import datetime
from ..models.products import Product, Category
from ..models.mainInventory import Warehouse, InventoryItem
from ..models.transactions import StockTransfer, TransferItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'main_unit', 'selling_price', 'is_active')
    list_filter = ('category', 'is_active', 'main_unit')
    search_fields = ('name', 'sku', 'barcode')
    
    fieldsets = (
        ('التعريف الأساسي', {
            'fields': ('category', 'name', 'sku', 'barcode', 'is_active', 'image')
        }),
        ('نظام الوحدات المتداخلة', {
            'description': "الوحدات من الأصغر للأكبر. مثال: قطعة -> دستة (12 قطعة) -> كرتونة (144 قطعة)",
            'fields': (
                ('base_unit', 'sub_unit', 'main_unit'),
                ('conversion_factor_sub', 'conversion_factor_main')
            )
        }),
        ('التسعير (للكرتونة)', {
            'fields': (('base_price', 'selling_price'),)
        }),
        ('الأبعاد والخصائص', {
            'classes': ('collapse',), # قابلة للطي، اضغط "إظهار" لرؤيتها
            'fields': (('weight', 'length', 'width', 'height'), ('size', 'color'))
        }),
    )

    class Media:
        js = (
            'https://unpkg.com/html5-qrcode',
            'js/admin_barcode_scanner.js',
        )

# 🆕 أصناف التحويل (الجدول الفرعي داخل إذن التحويل)
class TransferItemInline(admin.TabularInline):
    model = TransferItem
    extra = 1
    # الحقول تشمل الوحدة المختارة لضمان دقة التحويل
    fields = ('product', 'selected_unit', 'quantity', 'is_received')

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse_type', 'assigned_rep', 'is_active')
    list_filter = ('warehouse_type', 'is_active')

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'get_stock_display')
    list_filter = ('warehouse', 'product__category')
    search_fields = ('product__name', 'product__sku')

    def get_stock_display(self, obj):
        return f"{obj.stock_quantity} قطعة"
    get_stock_display.short_description = "الرصيد المتاح"

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('transfer_no', 'sender_warehouse', 'receiver_warehouse', 'status', 'created_at')
    list_filter = ('status', 'sender_warehouse', 'receiver_warehouse')
    search_fields = ('transfer_no', 'notes')
    inlines = [TransferItemInline]

    # تصحيح دالة الحفظ التلقائي لكود التحويل
    def save_model(self, request, obj, form, change):
        if not obj.transfer_no:
            # توليد رقم إذن تلقائي بناءً على التاريخ والوقت
            obj.transfer_no = f"TRF-{datetime.datetime.now().strftime('%y%m%d%H%M')}"
        # تم تصحيح super().save إلى super().save_model لمنع الـ AttributeError
        super().save_model(request, obj, form, change)

