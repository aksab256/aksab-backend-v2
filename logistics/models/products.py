from django.db import models

class Product(models.Model):
    UNIT_CHOICES = [
        ('PCS', 'قطعة'),
        ('BOX', 'كرتونة'),
        ('KG', 'كيلو'),
    ]

    name = models.CharField(max_length=255, verbose_name="اسم المنتج")
    sku = models.CharField(max_length=50, unique=True, verbose_name="كود الصنف (SKU)")
    barcode = models.CharField(max_length=100, blank=True, null=True, verbose_name="باركود")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='PCS', verbose_name="وحدة القياس")
    
    # الأسعار (لوجستياً)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر التكلفة")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر البيع للجمهور")
    
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="صورة المنتج")
    is_active = models.BooleanField(default=True, verbose_name="متاح للبيع")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"

    def __str__(self):
        return f"{self.name} ({self.sku})"

