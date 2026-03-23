from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class RepresentativeVault(models.Model):
    """محفظة العهدة النقدية للمندوب - Cash in Hand"""
    representative = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vault',
        verbose_name="المندوب"
    )
    current_cash_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, 
        verbose_name="العهدة النقدية الحالية (في يده)"
    )
    last_clearance_date = models.DateTimeField(
        null=True, blank=True, verbose_name="تاريخ آخر تصفية حساب"
    )

    class Meta:
        verbose_name = "محفظة مندوب"
        verbose_name_plural = "محافظ المناديب (العهدة النقدية)"

    def __str__(self):
        return f"محفظة {self.representative.username} - رصيد: {self.current_cash_balance}"

class CollectionAction(models.Model):
    """سجل حركات التحصيل والعهدة"""
    ACTION_TYPES = [
        ('INVOICE_CASH', 'مبيعات فاتورة كاش'),
        ('DEBT_COLLECTION', 'تحصيل مديونية'),
        ('CLEARANCE', 'تصفية عهدة (توريد للخزنة)'),
    ]
    
    STATUS_CHOICES = [
        ('HOLD', 'في عهدة المندوب'),
        ('SETTLED', 'تم التوريد للمركز الرئيسي'),
        ('CANCELLED', 'ملغى'),
    ]

    vault = models.ForeignKey(RepresentativeVault, on_delete=models.CASCADE, related_name='actions')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="المبلغ")
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='HOLD')
    
    # ربط اختياري بالفاتورة (لو كانت الحركة ناتجة عن بيع)
    invoice = models.ForeignKey(
        'Invoice', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الفاتورة"
    )
    
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="القائم بالحركة"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    settled_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ التوريد الفعلي")

    class Meta:
        verbose_name = "حركة تحصيل/توريد"
        verbose_name_plural = "سجل حركات النقدية"

class CompanyTreasury(models.Model):
    """الخزينة الرئيسية للشركة"""
    name = models.CharField(max_length=100, default="الخزينة المركزية")
    total_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "الخزينة الرئيسية"
        verbose_name_plural = "الخزينة الرئيسية"

    def __str__(self):
        return f"{self.name} - الرصيد الحالي: {self.total_balance}"

