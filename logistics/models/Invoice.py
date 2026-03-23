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
    warehouse = models.ForeignKey('Warehouse', on_delete=models.PROTECT, verbose_name="المخزن (السحب من)", null=True, blank=False)
    
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
        """تحديث الحسابات وضبط رصيد العميل بناءً على نوع الدفع"""
        with transaction.atomic():
            # 1. حساب الإجماليات من الأصناف
            aggregate = self.items.aggregate(total=models.Sum('line_total'))
            new_total_before = aggregate['total'] or 0
            new_final_total = new_total_before - self.discount_amount
            
            # 2. ضبط المبلغ المدفوع والمتبقي بناءً على نوع الفاتورة
            if self.payment_method == 'cash':
                self.paid_amount = new_final_total
                new_remaining = 0
            else:
                new_remaining = new_final_total - self.paid_amount

            # 3. حساب الفرق لتحديث رصيد العميل (فقط للفواتير غير النقدية)
            # نستخدم التحديث بالفرق (diff) لضمان دقة الرصيد عند تعديل الفاتورة
            diff = new_remaining - self.remaining_amount
            
            # 4. تحديث الفاتورة في قاعدة البيانات
            Invoice.objects.filter(pk=self.pk).update(
                total_before_discount=new_total_before,
                final_total=new_final_total,
                paid_amount=self.paid_amount,
                remaining_amount=new_remaining
            )
            
            # 5. تحديث رصيد العميل (فقط إذا كانت الفاتورة آجل أو جزئي)
            if self.payment_method != 'cash':
                customer = self.customer
                customer.current_balance += diff
                customer.save()
            
            # تحديث الكائن الحالي في الذاكرة
            self.remaining_amount = new_remaining

    def clean(self):
        """فحص حد الائتمان والمخزن"""
        if not self.warehouse:
            raise ValidationError("⚠️ يجب اختيار المخزن الذي سيتم السحب منه.")
            
        # منع البيع الآجل لو العميل متجاوز الحد
        if self.payment_method != 'cash':
            if self.customer.credit_limit > 0 and self.customer.current_balance >= self.customer.credit_limit:
                raise ValidationError(f"⚠️ العميل متجاوز لحد الائتمان المسموح.")
            
            overdue_limit = timezone.now() - timedelta(days=self.customer.credit_days_limit)
            if Invoice.objects.filter(customer=self.customer, remaining_amount__gt=0, date_created__lt=overdue_limit).exists():
                raise ValidationError(f"⚠️ العميل لديه فواتير متأخرة تجاوزت المدة المسموحة.")

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            self.invoice_no = f"INV-{timezone.now().strftime('%y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_no} - {self.customer.name}"

    class Meta:
        verbose_name = "فاتورة بيع"
        verbose_name_plural = "فواتير البيع"
        ordering = ['-date_created']

