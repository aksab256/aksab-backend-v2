from django.contrib import admin
from django.utils.html import format_html
from django import forms
from ..models.mainInventory import Warehouse, InventoryItem
from ..models.products import Product
from ..models.transactions import StockTransfer

# --- 1. إدارة المنتجات ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'unit', 'selling_price', 'is_active')
    search_fields = ('name', 'sku', 'barcode')
    list_filter = ('unit', 'is_active')

# --- 2. إدارة المخازن (الرئيسي والسيارات) ---
class InventoryInline(admin.TabularInline):
    model = InventoryItem
    extra = 1
    readonly_fields = ('last_updated',)

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse_type', 'assigned_rep', 'is_active', 'view_inventory_link')
    list_filter = ('warehouse_type', 'is_active')
    search_fields = ('name', 'assigned_rep__user__first_name')
    raw_id_fields = ('assigned_rep',)
    inlines = [InventoryInline]

    def view_inventory_link(self, obj):
        return format_html('<a href="/admin/logistics/inventoryitem/?warehouse__id__exact={}">عرض الجرد 📦</a>', obj.id)
    view_inventory_link.short_description = "محتويات المخزن"

# --- 3. إدارة الجرد (تأمين العهدة) ---
@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    # تم تعديل list_display ليشمل stock_quantity مباشرة لحل مشكلة admin.E122
    list_display = ('product', 'warehouse', 'stock_quantity', 'colored_status', 'last_updated')
    list_filter = ('warehouse', 'warehouse__warehouse_type', 'product')
    search_fields = ('product__name', 'warehouse__name')
    list_editable = ('stock_quantity',) # الآن سيعمل بدون أخطاء

    def colored_status(self, obj):
        if obj.stock_quantity <= 0:
            return format_html('<span style="color: red; font-weight: bold;">نفذت الكمية ⚠️</span>')
        elif obj.stock_quantity <= 10:
            return format_html('<span style="color: orange; font-weight: bold;">كمية منخفضة 📉</span>')
        return format_html('<span style="color: green; font-weight: bold;">متوفر ✅</span>')
    colored_status.short_description = "حالة المخزون"

# --- 4. إدارة تحويلات العهد (الربط الأوتوماتيكي) ---
@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender_warehouse', 'receiver_warehouse', 'product', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'sender_warehouse', 'receiver_warehouse')
    search_fields = ('product__name', 'sender_warehouse__name', 'receiver_warehouse__name')
    list_editable = ('status',) # بمجرد تغييرها لـ COMPLETED يتم التحويل أوتوماتيكياً

