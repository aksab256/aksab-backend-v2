from django.contrib import admin
from ..models.products import Product, Category
from ..models.mainInventory import Warehouse, InventoryItem
from ..models.transactions import StockTransfer, TransferItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # عرض البيانات المهمة في القائمة الرئيسية
    list_display = ('name', 'sku', 'category', 'base_unit', 'selling_price', 'is_active')
    list_filter = ('category', 'is_active', 'base_unit')
    search_fields = ('name', 'sku', 'barcode')

    # تقسيم الصفحة لمجموعات (Fieldsets)
    fieldsets = (
        ('التعريف الأساسي', {
            'fields': ('category', 'name', 'sku', 'barcode', 'is_active', 'image')
        }),
        ('نظام الوحدات المتداخلة', {
            'description': "حدد الوحدات من الأصغر للأكبر ومعامل التحويل بينهما",
            'fields': (
                ('base_unit', 'sub_unit', 'main_unit'),
                ('conversion_factor_sub', 'conversion_factor_main')
            )
        }),
        ('الشحن والخدمات اللوجستية (الأبعاد والوزن)', {
            'fields': (('weight', 'length'), ('width', 'height'))
        }),
        ('المقاس واللون (للملابس والأصناف المتنوعة)', {
            'fields': (('size', 'color'),)
        }),
        ('التسعير الأساسي', {
            'fields': (('base_price', 'selling_price'),)
        }),
    )

    # 🚀 تصحيح: الـ Media لازم تكون "جوه" الـ ProductAdmin
    class Media:
        js = (
            'https://unpkg.com/html5-qrcode',  # مكتبة الـ Scanner الخارجية
            'js/admin_barcode_scanner.js',     # ملف السكريبت المحلي
        )

class TransferItemInline(admin.TabularInline):
    model = TransferItem
    extra = 1
    fields = ('product', 'quantity', 'unit_at_transfer', 'is_received')

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse_type', 'is_active')

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'stock_quantity')
    list_filter = ('warehouse',)
    search_fields = ('product__name', 'product__sku')

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('transfer_no', 'sender_warehouse', 'status', 'created_at')
    list_filter = ('status', 'sender_warehouse')
    inlines = [TransferItemInline]

