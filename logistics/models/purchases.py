# logistics/models/purchases.py

from django.db import models, transaction
from .products import Product
from .mainInventory import Warehouse, InventoryItem

class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم المورد")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="الرصيد (له)")

    class Meta:
        verbose_name = "مورد"
        verbose_name_plural = "الموردين"

    def __str__(self): return self.name

class PurchaseInvoice(models.Model):
    invoice_no = models.CharField(max_length=100, unique=True, verbose_name="رقم فاتورة المورد")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="المورد")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن المستلم")
    date = models.DateField(verbose_name="تاريخ الاستلام")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="إجمالي الفاتورة")

    class Meta:
        verbose_name = "فاتورة شراء"
        verbose_name_plural = "فواتير الشراء"

class PurchaseItem(models.Model):
    invoice = models.ForeignKey(PurchaseInvoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity_in_main_unit = models.PositiveIntegerField(verbose_name="الكمية (بالكرتونة)")
    cost_price_per_main_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر شراء الكرتونة")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # 🚀 الحسبة الذكية: تحويل الكراتين لقطع عشان المخزن بيفهم أصغر وحدة
            total_pieces = self.quantity_in_main_unit * self.product.conversion_factor_main
            
            # تحديث رصيد المخزن الرئيسي المختار في الفاتورة
            inventory, created = InventoryItem.objects.get_or_create(
                warehouse=self.invoice.warehouse,
                product=self.product
            )
            inventory.stock_quantity += total_pieces
            inventory.save()
            
            super().save(*args, **kwargs)

