from django.contrib import admin
from ..models.product import Product
from ..models.mainInventory import Warehouse, InventoryItem
from ..models.transactions import StockTransfer, TransferItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'unit', 'selling_price')
    search_fields = ('name', 'sku')

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

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    # تم تصحيح list_display هنا (حذفنا product و quantity لأنهم في الـ Inline)
    list_display = ('transfer_no', 'sender_warehouse', 'status', 'created_at')
    list_filter = ('status', 'sender_warehouse')
    inlines = [TransferItemInline]

