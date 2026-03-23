from django.db import models, transaction
from django.conf import settings
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
# استيراد الموديلات الجديدة للربط
from .treasury import RepresentativeVault, CollectionAction

class Invoice(models.Model):
    PAYMENT_METHODS = [('cash', 'نقدي'), ('credit', 'آجل'), ('partial', 'جزئي')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_no = models.CharField(max_length=50, unique=True, verbose_name="رقم الفاتورة", blank=True)
    customer = models.ForeignKey('Customer', on_delete=models.PROTECT, related_name='invoices')
    
    # المخزن الذي تم سحب البضاعة منه
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
        """تحديث الحسابات، رصيد العميل، ومحفظة عهدة المندوب"""
        with transaction.atomic():
            # 1. حساب الإجماليات من الأصناف المرتبطة
            aggregate = self.items.aggregate(total=models.Sum('line_total'))
            new_total_before = aggregate['total'] or 0
            new_final_total = new_total_before - self.discount_amount
            
            # 2. ضبط المبالغ بناءً على طريقة الدفع
            if self.payment_method == 'cash':
                self.paid_amount = new_final_total
                new_remaining = 0
            else:
                new_remaining = new_final_total - self.paid_amount

            # 3. حساب فروق الأرصدة للتحديث (لتجنب التكرار عند التعديل)
            diff_customer = new_remaining - self.remaining_amount
            
            # 4. تحديث بيانات الفاتورة الأساسية
            Invoice.objects.filter(pk=self.pk).update(
                total_before_discount=new_total_before,
                final_total=new_final_total,
                paid_amount=self.paid_amount,
                remaining_amount=new_remaining
            )
            
            # 5. التعامل مع مديونية العميل (فقط في الآجل أو الجزئي)
            if self.payment_method != 'cash':
                customer = self.customer
                customer.current_balance += diff_customer
                customer.save()

            # 6. التعامل مع عهدة المندوب (في حالة وجود مبلغ مدفوع كاش)
            if self.paid_amount > 0:
                # الحصول على محفظة المندوب (أو إنشاؤها إذا لم توجد)
                vault, _ = RepresentativeVault.objects.get_or_create(representative=self.salesman)
                
                # تسجيل حركة "تحصيل نقدية" أو تحديثها
                # نستخدم update_or_create بناءً على الفاتورة لضمان عدم تكرار العهدة عند تعديل نفس الفاتورة
                action, created = CollectionAction.objects.update_or_create(
                    invoice=self,
                    defaults={
                        'vault': vault,
                        'amount': self.paid_amount,
                        'action_type': 'INVOICE_CASH' if self.payment_method == 'cash' else 'DEBT_COLLECTION',
                        'collector': self.salesman,
                        'status': 'HOLD'
                    }
                )
                
                # تحديث رصيد المحفظة الفعلي (العهدة التي في يد المندوب)
                # ملاحظة: الحسبة هنا تحتاج مراعاة الفرق في حالة التعديل، لكن للتبسيط في الفاتورة الجديدة:
                # سنقوم بإعادة حساب إجمالي المحفظة من الحركات غير الموردة (HOLD) لضمان الدقة المطلقة
                total_hold = CollectionAction.objects.filter(
                    vault=vault, 
                    status='HOLD'
                ).aggregate(total=models.Sum('amount'))['total'] or 0
                
                vault.current_cash_balance = total_hold
                vault.save()

            # تحديث القيم في الكائن الحالي بالذاكرة
            self.remaining_amount = new_remaining

    def clean(self):
        """التحقق من صحة البيانات قبل الحفظ"""
        if not self.warehouse:
            raise ValidationError("⚠️ يجب اختيار المخزن الذي سيتم السحب منه.")
            
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

