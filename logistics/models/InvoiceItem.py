from django.db import models
from django.core.validators import MinValueValidator

class InvoiceItem(models.Model):
    # ربط الفاتورة (استخدمنا اسم الموديل كـ String لتجنب مشاكل الـ Import)
    invoice = models.ForeignKey(
        'Invoice', 
        related_name='items', 
        on_delete=models.CASCADE,
        verbose_name="الفاتورة"
    )
    
    # ربط المنتج
    product = models.ForeignKey(
        'Product', 
        on_delete=models.PROTECT,
        verbose_name="المنتج"
    )
    
    # تسجيل السعر والخصم وقت البيع (لحماية الفاتورة من تغيرات الأسعار لاحقاً)
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="سعر الوحدة"
    )
    
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], 
        verbose_name="الكمية"
    )
    
    discount_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="خصم الوحدة"
    )
    
    line_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        editable=False, 
        verbose_name="إجمالي السطر"
    )

    def save(self, *args, **kwargs):
        # حساب إجمالي السطر أوتوماتيكياً (الكمية * (السعر - الخصم))
        self.line_total = self.quantity * (self.unit_price - self.discount_per_unit)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "صنف فاتورة"
        verbose_name_plural = "أصناف الفواتير"

