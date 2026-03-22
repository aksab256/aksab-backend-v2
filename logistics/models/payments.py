from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from .Invoice import Invoice

class Collection(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.PROTECT, related_name='payments', verbose_name="العميل")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', null=True, blank=True, verbose_name="الفاتورة (اختياري)")
    collector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="المحصل / المندوب")
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="المبلغ المحصل")
    collection_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التحصيل")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    def clean(self):
        # منع تحصيل مبلغ أكبر من مديونية العميل الكلية
        if self.amount > self.customer.current_balance:
            raise ValidationError(f"❌ لا يمكن تحصيل مبلغ ({self.amount}) أكبر من مديونية العميل ({self.customer.current_balance})")
        
        # لو التحصيل مرتبط بفاتورة معينة، نأكد إن المبلغ ميزيدش عن المتبقي فيها
        if self.invoice and self.amount > self.invoice.remaining_amount:
            raise ValidationError(f"❌ المبلغ أكبر من المتبقي في الفاتورة ({self.invoice.remaining_amount})")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            is_new = self.pk is None
            self.full_clean()
            super().save(*args, **kwargs)
            
            if is_new:
                # 1. تحديث الفاتورة (لو موجودة)
                if self.invoice:
                    self.invoice.paid_amount += self.amount
                    self.invoice.remaining_amount -= self.amount
                    self.invoice.save()
                
                # 2. تحديث حساب العميل (تلقائياً)
                customer = self.customer
                customer.current_balance -= self.amount
                customer.total_paid += self.amount
                customer.save()

    class Meta:
        verbose_name = "عملية تحصيل"
        verbose_name_plural = "التحصيلات"

