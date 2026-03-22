from django.db import models
from django.conf import settings

class Customer(models.Model):
    # بيانات الهوية
    name = models.CharField(max_length=255, verbose_name="اسم المحل / العميل")
    owner_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="اسم صاحب المحل")
    phone = models.CharField(max_length=20, unique=True, verbose_name="رقم الهاتف")
    alt_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم هاتف إضافي")

    # بيانات الموقع
    address = models.TextField(verbose_name="العنوان المكتوب")
    latitude = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name="خط العرض")
    longitude = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name="خط الطول")

    # التصنيف
    customer_type = models.CharField(max_length=50, choices=[
        ('RETAIL', 'قطاعي'),
        ('WHOLESALE', 'جملة'),
        ('SUPERMARKET', 'سوبر ماركت'),
    ], default='RETAIL')

    # الربط بالمندوب
    assigned_rep = models.ForeignKey(
        'SalesRepresentative',
        on_delete=models.SET_NULL,
        null=True,
        related_name='my_customers',
        verbose_name="المندوب المسؤول"
    )

    # بيانات مالية متطورة
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="حد الائتمان (مبلغ)")
    credit_days_limit = models.PositiveIntegerField(default=30, verbose_name="حد الائتمان (بالأيام)")
    
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="المديونية الحالية")
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="إجمالي التحصيلات")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"

