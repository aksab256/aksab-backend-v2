from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

class Invoice(models.Model):
    PAYMENT_METHODS = [('cash', 'نقدي'), ('credit', 'آجل'), ('partial', 'جزئي')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_no = models.CharField(max_length=50, unique=True, verbose_name="رقم الفاتورة", blank=True)
    
    customer = models.ForeignKey('Customer', on_delete=models.PROTECT, related_name='invoices')
    salesman = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sales_invoices')
    collector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    
    date_created = models.DateTimeField(auto_now_add=True)
    
    total_before_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="خصم إضافي")
    final_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def clean(self):
        """منطق منع البيع في حالة تجاوز حدود الائتمان"""
        if self.payment_method != 'cash':
            # 1. فحص حد الائتمان النقدي
            new_balance = self.customer.current_balance + self.remaining_amount
            if self.customer.credit_limit > 0 and new_balance > self.customer.credit_limit:
                raise ValidationError(f"⚠️ تجاوز حد الائتمان النقدي! المديونية ستصبح {new_balance} والحد المسموح {self.customer.credit_limit}")

            # 2. فحص حد الائتمان الزمني (البحث عن فواتير قديمة لم تسدد)
            overdue_limit = timezone.now() - timedelta(days=self.customer.credit_days_limit)
            has_overdue = Invoice.objects.filter(
                customer=self.customer,
                remaining_amount__gt=0,
                date_created__lt=overdue_limit
            ).exists()
            
            if has_overdue:
                raise ValidationError(f"⚠️ تجاوز حد الائتمان الزمني! العميل لديه فواتير متأخرة لم تسدد منذ أكثر من {self.customer.credit_days_limit} يوم.")

    def update_totals(self):
        aggregate = self.items.aggregate(total=models.Sum('line_total'))
        self.total_before_discount = aggregate['total'] or 0
        self.final_total = self.total_before_discount - self.discount_amount
        self.remaining_amount = self.final_total - self.paid_amount
        Invoice.objects.filter(pk=self.pk).update(
            total_before_discount=self.total_before_discount,
            final_total=self.final_total,
            remaining_amount=self.remaining_amount
        )

    def save(self, *args, **kwargs):
        # استدعاء الفحص قبل الحفظ
        self.full_clean()
        if not self.invoice_no:
            self.invoice_no = f"INV-{timezone.now().strftime('%y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "فاتورة بيع"
        ordering = ['-date_created']

