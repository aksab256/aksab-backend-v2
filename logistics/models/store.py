# logistics/models/store.py
from django.db import models
from django.conf import settings # لاستيراد موديل المستخدم الافتراضي

class Store(models.Model):
    # ربط المحل بالمستخدم (المالك) - ForeignKey بتعمل قائمة منسدلة في الـ Admin
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='stores',
        verbose_name="المالك"
    )
    
    supermarket_name = models.CharField(max_length=255, verbose_name="اسم المتجر")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_visible_in_store = models.BooleanField(default=True, verbose_name="مرئي للعملاء")
    
    # الموقع الجغرافي
    latitude = models.FloatField(null=True, blank=True, verbose_name="خط العرض")
    longitude = models.FloatField(null=True, blank=True, verbose_name="خط الطول")
    
    store_type = models.CharField(
        max_length=50, 
        default='supermarket',
        choices=[
            ('supermarket', 'سوبر ماركت'),
            ('restaurant', 'مطعم / كافيه'),
            ('pharmacy', 'صيدلية'),
            ('vegetables', 'خضروات وفاكهة'),
        ],
        verbose_name="نوع النشاط"
    )
    
    # تاريخ انتهاء الفترة التجريبية (إجباري)
    trial_expiry_date = models.DateTimeField(verbose_name="تاريخ انتهاء العهدة التجريبية")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.supermarket_name

    class Meta:
        verbose_name = "متجر"
        verbose_name_plural = "المتاجر"

