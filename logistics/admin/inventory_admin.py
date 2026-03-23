from django.contrib import admin
from django.urls import path
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
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
            'classes': ('collapse',),
            'fields': (('weight', 'length', 'width', 'height'), ('size', 'color'))
        }),
    )

    class Media:
        js = (
            'https://unpkg.com/html5-qrcode',
            'js/admin_barcode_scanner.js',
        )

class TransferItemInline(admin.TabularInline):
    model = TransferItem
    extra = 1
    fields = ('product', 'selected_unit', 'quantity', 'is_received')

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    # أضفنا view_inventory هنا
    list_display = ('name', 'warehouse_type', 'assigned_rep', 'is_active', 'view_inventory')
    list_filter = ('warehouse_type', 'is_active')
    search_fields = ('name',)

    # 1️⃣ زرار تقرير الأرصدة في جدول المخازن
    def view_inventory(self, obj):
        return format_html(
            '<a class="button" href="report/{}/" target="_blank" style="background-color: #417690; color: white; padding: 5px 10px; border-radius: 4px;">تقرير الأرصدة 📦</a>',
            obj.pk
        )
    view_inventory.short_description = "الأرصدة الحالية"

    # 2️⃣ تسجيل الـ URL الخاص بالتقرير
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('report/<int:warehouse_id>/', self.admin_site.admin_view(self.inventory_report_view)),
        ]
        return custom_urls + urls

    # 3️⃣ الدالة التي تجلب بيانات المخزون للمخزن المحدد
    def inventory_report_view(self, request, warehouse_id):
        warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
        # جلب الأصناف المربوطة بهذا المخزن مع بيانات المنتج
        inventory_items = InventoryItem.objects.filter(warehouse=warehouse).select_related('product', 'product__category')
        
        context = {
            'warehouse': warehouse,
            'inventory_items': inventory_items,
            'title': f"تقرير أرصدة مخزن: {warehouse.name}",
        }
        return render(request, 'admin/logistics/inventory_report.html', context)

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

    def save_model(self, request, obj, form, change):
        if not obj.transfer_no:
            obj.transfer_no = f"TRF-{datetime.datetime.now().strftime('%y%m%d%H%M')}"
        super().save_model(request, obj, form, change)

