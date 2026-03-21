from django.db import models
# استدعاء موديل المندوب من ملفه المجاور
from .sales_rep import SalesRepresentative
# استدعاء موديل المنتجات الجديد (تأكد من إنشاء ملف products.py)
from .products import Product

class Warehouse(models.Model):
    MAIN_WH = 'MAIN'
    VAN_WH = 'VAN'
    TYPES = [
        (MAIN_WH, 'المخزن الرئيسي'),
        (VAN_WH, 'مخزن سيارة المندوب'),
    ]

    name = models.CharField(max_length=150, verbose_name="اسم المخزن/السيارة")
    warehouse_type = models.CharField(max_length=10, choices=TYPES, default=MAIN_WH)
    
    # الربط بموديل SalesRepresentative
    assigned_rep = models.OneToOneField(
        SalesRepresentative, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='van_warehouse',
        verbose_name="المندوب المسؤول"
    )

    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مخزن"
        verbose_name_plural = "المخازن"

    def __str__(self):
        return f"{self.name} - {self.get_warehouse_type_display()}"

class InventoryItem(models.Model):
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name='inventory_items',
        verbose_name="المخزن"
    )
    # الربط المباشر بموديل المنتج الجديد
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='stock_records',
        verbose_name="المنتج"
    )
    stock_quantity = models.IntegerField(default=0, verbose_name="الكمية الحالية")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('warehouse', 'product')
        verbose_name = "صنف بالمخزن"
        verbose_name_plural = "جرد المخازن"

    def __str__(self):
        return f"{self.product.name} ({self.warehouse.name}): {self.stock_quantity}"

