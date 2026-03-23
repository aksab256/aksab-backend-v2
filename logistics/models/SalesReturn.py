import datetime
from django.db import models, transaction
from django.core.exceptions import ValidationError
from .mainInventory import InventoryItem

class SalesReturn(models.Model):
    return_no = models.CharField(max_length=50, unique=True, verbose_name="رقم المرتجع", blank=True)
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='returns', verbose_name="الفاتورة الأصلية")
    date_returned = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ المرتجع")
    reason = models.TextField(blank=True, null=True, verbose_name="سبب المرتجع")
    total_return_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="إجمالي قيمة المرتجع")

    class Meta:
        verbose_name = "مرتجع مبيعات"
        verbose_name_plural = "مرتجعات المبيعات"

    def __str__(self):
        return f"مرتجع {self.return_no} لـ {self.invoice.invoice_no}"

    def save(self, *args, **kwargs):
        if not self.return_no:
            self.return_no = f"RET-{datetime.datetime.now().strftime('%y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

class SalesReturnItem(models.Model):
    UNIT_CHOICES = [
        ('main', 'وحدة كبرى (كرتونة)'),
        ('sub', 'وحدة متوسطة (دستة/ربطة)'),
        ('base', 'وحدة صغرى (قطعة)'),
    ]

    sales_return = models.ForeignKey(SalesReturn, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.PROTECT, verbose_name="الصنف المرتجع")
    
    # 🆕 اختيار الوحدة المرتجعة (مهم جداً للسيناريو بتاعك)
    selected_unit = models.CharField(
        max_length=10, 
        choices=UNIT_CHOICES, 
        default='base', 
        verbose_name="الوحدة المرجعة"
    )
    
    quantity = models.PositiveIntegerField(verbose_name="الكمية المرتجعة")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="سعر الوحدة عند المرتجع")
    line_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # 1. تحديد المعامل والسعر التلقائي بناءً على الوحدة المرجعة
            if self.selected_unit == 'main':
                factor = self.product.conversion_factor_main
                default_price = self.product.selling_price
            elif self.selected_unit == 'sub':
                factor = self.product.conversion_factor_sub
                default_price = self.product.price_per_sub_unit
            else:
                factor = 1
                default_price = self.product.price_per_piece

            # لو اليوزر مأدخلش سعر المرتجع، السيستم بيحسبه أوتوماتيك
            if not self.unit_price:
                self.unit_price = default_price

            # 2. حساب القيمة المالية للمرتجع
            self.line_total = self.quantity * self.unit_price

            # 3. التأثير على المخزن (زيادة الرصيد بالقطع الصغيرة)
            target_warehouse = self.sales_return.invoice.warehouse
            if target_warehouse:
                inventory, created = InventoryItem.objects.get_or_create(
                    warehouse=target_warehouse,
                    product=self.product,
                    defaults={'stock_quantity': 0}
                )

                total_pieces = self.quantity * factor
                
                # في حالة التعديل على سجل المرتجع نفسه
                if self.pk:
                    old_item = SalesReturnItem.objects.get(pk=self.pk)
                    old_factor = self.product.conversion_factor_main if old_item.selected_unit == 'main' else \
                                 self.product.conversion_factor_sub if old_item.selected_unit == 'sub' else 1
                    inventory.stock_quantity -= (old_item.quantity * old_factor)

                inventory.stock_quantity += total_pieces
                inventory.save()

            # 4. التأثير على حساب العميل (تخفيض مديونيته)
            customer = self.sales_return.invoice.customer
            # لو تعديل: بنرجع الفرق
            if self.pk:
                old_item = SalesReturnItem.objects.get(pk=self.pk)
                customer.current_balance += old_item.line_total # نلغي الخصم القديم
            
            customer.current_balance -= self.line_total # نخصم المرتجع الجديد
            customer.save()

            super().save(*args, **kwargs)

            # 5. تحديث إجمالي المرتجع في الموديل الأب
            new_total = self.sales_return.items.aggregate(total=models.Sum('line_total'))['total'] or 0
            SalesReturn.objects.filter(pk=self.sales_return.pk).update(total_return_amount=new_total)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            # عند حذف سجل المرتجع: البضاعة تخرج من المخزن تاني ومديونية العميل تزيد تاني
            factor = self.product.conversion_factor_main if self.selected_unit == 'main' else \
                     self.product.conversion_factor_sub if self.selected_unit == 'sub' else 1
            
            inventory = InventoryItem.objects.filter(
                warehouse=self.sales_return.invoice.warehouse, 
                product=self.product
            ).first()
            if inventory:
                inventory.stock_quantity -= (self.quantity * factor)
                inventory.save()

            customer = self.sales_return.invoice.customer
            customer.current_balance += self.line_total
            customer.save()

            sales_return = self.sales_return
            super().delete(*args, **kwargs)
            
            # تحديث الإجمالي النهائي للمرتجع
            new_total = sales_return.items.aggregate(total=models.Sum('line_total'))['total'] or 0
            SalesReturn.objects.filter(pk=sales_return.pk).update(total_return_amount=new_total)

    class Meta:
        verbose_name = "صنف مرتجع"

