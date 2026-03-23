from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from .mainInventory import InventoryItem

class InvoiceItem(models.Model):
    UNIT_CHOICES = [
        ('main', 'وحدة كبرى (كرتونة)'),
        ('sub', 'وحدة متوسطة (دستة/ربطة)'),
        ('base', 'وحدة صغرى (قطعة)'),
    ]

    invoice = models.ForeignKey('Invoice', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.PROTECT, verbose_name="المنتج")
    
    selected_unit = models.CharField(
        max_length=10, 
        choices=UNIT_CHOICES, 
        default='base', 
        verbose_name="الوحدة المباعة"
    )
    
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="السعر")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="الكمية")
    discount_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="خصم/وحدة")
    
    line_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # 1. تحديد معامل التحويل والسعر بناءً على الوحدة
            if self.selected_unit == 'main':
                factor = self.product.conversion_factor_main
                default_price = self.product.selling_price
            elif self.selected_unit == 'sub':
                factor = self.product.conversion_factor_sub
                default_price = self.product.price_per_sub_unit
            else:
                factor = 1
                default_price = self.product.price_per_piece

            if not self.unit_price:
                self.unit_price = default_price

            # 2. حساب إجمالي السطر
            self.line_total = self.quantity * (self.unit_price - self.discount_per_unit)

            # 3. تحديث المخزن (بالقطع الصغيرة)
            target_warehouse = self.invoice.warehouse
            if target_warehouse:
                inventory, created = InventoryItem.objects.get_or_create(
                    warehouse=target_warehouse,
                    product=self.product,
                    defaults={'stock_quantity': 0}
                )

                total_pieces = self.quantity * factor
                
                # إرجاع الكمية القديمة في حالة التعديل
                if self.pk:
                    old_item = InvoiceItem.objects.get(pk=self.pk)
                    old_factor = self.product.conversion_factor_main if old_item.selected_unit == 'main' else \
                                 self.product.conversion_factor_sub if old_item.selected_unit == 'sub' else 1
                    inventory.stock_quantity += (old_item.quantity * old_factor)

                if inventory.stock_quantity < total_pieces:
                    raise ValidationError(
                        f"⚠️ عجز في مخزن ({target_warehouse.name}) للصنف {self.product.name}. "
                        f"المتاح {inventory.stock_quantity} قطعة، والمطلوب {total_pieces} قطعة."
                    )
                
                inventory.stock_quantity -= total_pieces
                inventory.save()
            else:
                raise ValidationError("⚠️ لم يتم تحديد مخزن في الفاتورة للسحب منه!")

            super().save(*args, **kwargs)
            self.invoice.update_totals()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            target_warehouse = self.invoice.warehouse
            if target_warehouse:
                inventory = InventoryItem.objects.filter(warehouse=target_warehouse, product=self.product).first()
                if inventory:
                    factor = self.product.conversion_factor_main if self.selected_unit == 'main' else \
                             self.product.conversion_factor_sub if self.selected_unit == 'sub' else 1
                    inventory.stock_quantity += (self.quantity * factor)
                    inventory.save()
            
            invoice = self.invoice
            super().delete(*args, **kwargs)
            invoice.update_totals()

    def __str__(self):
        return f"{self.product.name} ({self.quantity} {self.get_selected_unit_display()})"

    class Meta:
        verbose_name = "صنف فاتورة"
        verbose_name_plural = "أصناف الفواتير"

