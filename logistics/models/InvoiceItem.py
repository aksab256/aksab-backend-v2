from django.db import models
from django.core.validators import MinValueValidator

class InvoiceItem(models.Model):
    invoice = models.ForeignKey('Invoice', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.PROTECT, verbose_name="المنتج")
    
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="السعر")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="الكمية")
    discount_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="خصم/قطعة")
    
    line_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # 1. سحب السعر من المنتج لو مش مكتوب يدوي
        if not self.unit_price:
            self.unit_price = self.product.selling_price
        
        # 2. حساب إجمالي السطر
        self.line_total = self.quantity * (self.unit_price - self.discount_per_unit)
        
        super().save(*args, **kwargs)
        
        # 3. نطلب من الفاتورة الأم تحديث إجمالياتها
        self.invoice.update_totals()

    class Meta:
        verbose_name = "صنف فاتورة"

