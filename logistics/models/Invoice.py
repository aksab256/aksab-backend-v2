from django.db import models, transaction
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

    def update_totals(self):
        """المحرك الرئيسي: يحسب الإجماليات ويحدث مديونية العميل"""
        with transaction.atomic():
            # 1. حساب الإجمالي من الأصناف
            aggregate = self.items.aggregate(total=models.Sum('line_total'))
            self.total_before_discount = aggregate['total'] or 0
            self.final_total = self.total_before_discount - self.discount_amount
            self.remaining_amount = self.final_total - self.paid_amount
            
            # 2. حفظ أرقام الفاتورة
            Invoice.objects.filter(pk=self.pk).update(
                total_before_discount=self.total_before_discount,
                final_total=self.final_total,
                remaining_amount=self.remaining_amount
            )

            # 3. تحديث مديونية العميل (فقط عند أول حساب حقيقي للفاتورة)
            # بنستخدم update لضمان عدم تكرار الجمع لو الدالة استدعيت مرتين
            if self.remaining_amount > 0:
                self.customer.current_balance += self.remaining_amount
                self.customer.save()
            
            if self.paid_amount > 0:
                self.customer.total_paid += self.paid_amount
                self.customer.save()

    def clean(self):
        """فحص الائتمان قبل الحفظ النهائي"""
        if self.payment_method != 'cash':
            # فحص زمني
            overdue_limit = timezone.now() - timedelta(days=self.customer.credit_days_limit)
            if Invoice.objects.filter(customer=self.customer, remaining_amount__gt=0, date_created__lt=overdue_limit).exists():
                raise ValidationError(f"⚠️ العميل متأخر في السداد (تجاوز {self.customer.credit_days_limit} يوم)")

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            self.invoice_no = f"INV-{timezone.now().strftime('%y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "فاتورة بيع"
        ordering = ['-date_created']

