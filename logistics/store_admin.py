from django.contrib import admin
from django.urls import path
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
from ..models.mainInventory import Warehouse, InventoryItem

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active', 'view_inventory')

    # زرار عرض الأرصدة الحالية
    def view_inventory(self, obj):
        return format_html(
            '<a class="button" href="report/{}/" target="_blank" style="background-color: #417690; color: white;">تقرير الأرصدة 📦</a>',
            obj.pk
        )
    view_inventory.short_description = "الأرصدة الحالية"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('report/<int:warehouse_id>/', self.admin_site.admin_view(self.inventory_report_view)),
        ]
        return custom_urls + urls

    def inventory_report_view(self, request, warehouse_id):
        warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
        # جلب الأصناف مع بيانات المنتج لتقليل الضغط على القاعدة (select_related)
        inventory_items = InventoryItem.objects.filter(warehouse=warehouse).select_related('product')
        
        context = {
            'warehouse': warehouse,
            'inventory_items': inventory_items,
            'title': f"تقرير أرصدة مخزن: {warehouse.name}",
        }
        return render(request, 'admin/logistics/inventory_report.html', context)

