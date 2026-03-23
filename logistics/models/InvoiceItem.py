from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from .mainInventory import InventoryItem

class InvoiceItem(models.Model):
    invoice = models.ForeignKey('Invoice', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.PROTECT, verbose_name="المنتج")
    
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="السعر")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="الكمية")
    discount_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="خصم/قطعة")
    
    line_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # 1. تحديد السعر الافتراضي لو لم يتم إدخاله
            if not self.unit_price:
                self.unit_price = self.product.selling_price

            # 2. حساب إجمالي السطر المالي
            self.line_total = self.quantity * (self.unit_price - self.discount_per_unit)

            # 3. منطق تحديث المخزن (مخزن الفاتورة المحدد)
            target_warehouse = self.invoice.warehouse
            if target_warehouse:
                inventory, created = InventoryItem.objects.get_or_create(
                    warehouse=target_warehouse,
                    product=self.product,
                    defaults={'stock_quantity': 0}
                )

                # تحويل كمية الفاتورة لقطع صغيرة بناءً على معامل التحويل
                total_pieces = self.quantity * self.product.conversion_factor_main
                
                # 🔄 في حالة التعديل: بنرجع الكمية القديمة للمخزن أولاً عشان نحسب من جديد
                if self.pk:
                    old_item = InvoiceItem.objects.get(pk=self.pk)
                    old_pieces = old_item.quantity * old_item.product.conversion_factor_main
                    inventory.stock_quantity += old_pieces

                # ⚠️ التأكد من أن الرصيد يكفي
                if inventory.stock_quantity < total_pieces:
                    raise ValidationError(
                        f"⚠️ عجز في مخزن ({target_warehouse.name}) للصنف {self.product.name}. "
                        f"المتاح {inventory.stock_quantity} قطعة فقط."
                    )
                
                # الخصم الفعلي من المخزن
                inventory.stock_quantity -= total_pieces
                inventory.save()
            else:
                raise ValidationError("⚠️ لم يتم تحديد مخزن في الفاتورة للسحب منه!")

            # حفظ السجل
            super().save(*args, **kwargs)

            # 4. تحديث إجماليات الفاتورة ورصيد العميل
            self.invoice.update_totals()

    def delete(self, *args, **kwargs):
        """إرجاع البضاعة للمخزن عند مسح صنف من الفاتورة"""
        with transaction.atomic():
            target_warehouse = self.invoice.warehouse
            if target_warehouse:
                inventory = InventoryItem.objects.filter(
                    warehouse=target_warehouse, 
                    product=self.product
                ).first()
                if inventory:
                    total_pieces = self.quantity * self.product.conversion_factor_main
                    inventory.stock_quantity += total_pieces
                    inventory.save()
            
            invoice = self.invoice
            super().delete(*args, **kwargs)
            # تحديث الفاتورة الأم مالياً بعد الحذف
            invoice.update_totals()

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    class Meta:
        verbose_name = "صنف فاتورة"
        verbose_name_plural = "أصناف الفواتير"

