from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid

class Invoice(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'نقدي'),
        ('credit', 'آجل'),
        ('partial', 'جزئي'),
    ]
    
    # معرف فريد للفاتورة (مفيد للربط مع فلاتر ومنع التكرار)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_no = models.CharField(max_length=50, unique=True, verbose_name="رقم الفاتورة")
    
    # الأطراف المعنية
    customer = models.ForeignKey('Customer', on_delete=models.PROTECT, related_name='invoices')
    salesman = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sales_invoices')
    collector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='collections')
    
    # التوقيت والمكان
    date_created = models.DateTimeField(auto_now_add=True)
    lat = models.FloatField(null=True, blank=True, verbose_name="خط العرض")
    lng = models.FloatField(null=True, blank=True, verbose_name="خط الطول")
    
    # الحسابات المالية
    total_before_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # تفاصيل الدفع
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # ملاحظات الزيارة
    notes = models.TextField(null=True, blank=True)
    is_synced_to_platform = models.BooleanField(default=False) # للربط مع المنصة مستقبلاً

    class Meta:
        verbose_name = "فاتورة بيع"
        ordering = ['-date_created']

    def save(self, *args, **kwargs):
        # حساب المتبقي أوتوماتيكياً قبل الحفظ
        self.remaining_amount = self.final_total - self.paid_amount
        super().save(*args, **kwargs)

