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
    
    # 🆕 إضافة المخزن في رأس الفاتورة لتحديد مصدر السحب
    warehouse = models.ForeignKey(
        'Warehouse', 
        on_delete=models.PROTECT, 
        verbose_name="المخزن (السحب من)",
        null=True, 
        blank=False
    )
    
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
        """تحديث الحسابات وتحديث رصيد العميل بالفرق فقط"""
        with transaction.atomic():
            # حساب الإجماليات الجديدة من الأصناف المرتبطة
            aggregate = self.items.aggregate(total=models.Sum('line_total'))
            new_total_before = aggregate['total'] or 0
            new_final_total = new_total_before - self.discount_amount
            new_remaining = new_final_total - self.paid_amount

            # 💡 السر هنا: حساب الفرق بين المتبقي القديم والجديد لتجنب تكرار الإضافة في رصيد العميل
            diff = new_remaining - self.remaining_amount
            
            # تحديث الفاتورة (استخدام filter.update أسرع ولا يستدعي save() مجدداً)
            Invoice.objects.filter(pk=self.pk).update(
                total_before_discount=new_total_before,
                final_total=new_final_total,
                remaining_amount=new_remaining
            )
            
            # تحديث الكائن الحالي في الذاكرة
            self.remaining_amount = new_remaining

            # تحديث رصيد العميل الحقيقي بالفرق
            customer = self.customer
            customer.current_balance += diff
            customer.save()

    def clean(self):
        """فحص حد الائتمان والمخزن قبل الحفظ النهائي"""
        if not self.warehouse:
            raise ValidationError("⚠️ يجب اختيار المخزن الذي سيتم السحب منه.")
            
        if not self.pk and self.payment_method != 'cash':
            if self.customer.credit_limit > 0 and self.customer.current_balance >= self.customer.credit_limit:
                raise ValidationError(f"⚠️ العميل متجاوز لحد الائتمان المسموح.")
            
            overdue_limit = timezone.now() - timedelta(days=self.customer.credit_days_limit)
            if Invoice.objects.filter(customer=self.customer, remaining_amount__gt=0, date_created__lt=overdue_limit).exists():
                raise ValidationError(f"⚠️ العميل لديه فواتير متأخرة تجاوزت المدة المسموحة.")

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            # توليد رقم فاتورة تلقائي بناءً على التاريخ
            self.invoice_no = f"INV-{timezone.now().strftime('%y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_no} - {self.customer.name}"

    class Meta:
        verbose_name = "فاتورة بيع"
        verbose_name_plural = "فواتير البيع"
        ordering = ['-date_created']

