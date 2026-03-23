from django.db import models, transaction
from django.core.exceptions import ValidationError
from .Invoice import Invoice
from .mainInventory import InventoryItem

class SalesReturn(models.Model):
    return_no = models.CharField(max_length=50, unique=True, verbose_name="رقم المرتجع", blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='returns', verbose_name="الفاتورة الأصلية")
    date_returned = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ المرتجع")
    reason = models.TextField(blank=True, null=True, verbose_name="سبب المرتجع")
    total_return_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="إجمالي قيمة المرتجع")

    def save(self, *args, **kwargs):
        if not self.return_no:
            import datetime
            self.return_no = f"RET-{datetime.datetime.now().strftime('%y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "مرتجع مبيعات"
        verbose_name_plural = "مرتجعات المبيعات"

    def __str__(self):
        return f"مرتجع {self.return_no} لـ {self.invoice.invoice_no}"

class SalesReturnItem(models.Model):
    sales_return = models.ForeignKey(SalesReturn, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.PROTECT, verbose_name="الصنف المرتجع")
    quantity = models.PositiveIntegerField(verbose_name="الكمية المرتجعة")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الوحدة عند المرتجع")
    line_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # 1. حساب القيمة المالية للمرتجع
            self.line_total = self.quantity * self.unit_price
            
            # 2. التأثير على المخزن (زيادة المخزن)
            # بنرجع البضاعة لنفس المخزن اللي خرجت منه الفاتورة الأصلية
            target_warehouse = self.sales_return.invoice.warehouse
            if target_warehouse:
                inventory, created = InventoryItem.objects.get_or_create(
                    warehouse=target_warehouse,
                    product=self.product
                )
                # تحويل لقطع صغيرة
                total_pieces = self.quantity * self.product.conversion_factor_main
                inventory.stock_quantity += total_pieces
                inventory.save()

            # 3. التأثير على حساب العميل (تخفيض المديونية)
            customer = self.sales_return.invoice.customer
            customer.current_balance -= self.line_total
            customer.save()

            super().save(*args, **kwargs)
            
            # 4. تحديث إجمالي مبلغ المرتجع في الموديل الأب
            new_total = self.sales_return.items.aggregate(total=models.Sum('line_total'))['total'] or 0
            SalesReturn.objects.filter(pk=self.sales_return.pk).update(total_return_amount=new_total)

    class Meta:
        verbose_name = "صنف مرتجع"

