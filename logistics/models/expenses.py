from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from .treasury import CompanyTreasury
import os

def expense_upload_path(instance, filename):
    # تنظيم الصور في فولدرات حسب السنة والشهر (expenses/2026/03/file.jpg)
    date = instance.date if instance.id else models.fields.timezone.now()
    return os.path.join('expenses', date.strftime('%Y/%m'), filename)

class ExpenseCategory(models.Model):
    """تصنيفات المصاريف (بنزين، إيجار، بوفيه...)"""
    name = models.CharField(max_length=100, verbose_name="نوع المصروف")

    class Meta:
        verbose_name = "تصنيف مصاريف"
        verbose_name_plural = "تصنيفات المصاريف"

    def __str__(self):
        return self.name

class Expense(models.Model):
    """سجل المصاريف الفعلي"""
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, verbose_name="نوع المصروف")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="المبلغ")
    date = models.DateField(auto_now_add=True, verbose_name="تاريخ الصرف")
    
    # 🆕 حقل صورة المستند
    receipt_image = models.ImageField(
        upload_to=expense_upload_path, 
        null=True, 
        blank=True, 
        verbose_name="صورة المستند / الإيصال"
    )
    
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات / بيان")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="المسؤول عن الصرف")

    def save(self, *args, **kwargs):
        from django.db import transaction
        with transaction.atomic():
            is_new = self.pk is None
            if is_new:
                # التأكد من وجود الخزينة وخصم المبلغ
                treasury = CompanyTreasury.objects.first()
                if not treasury:
                    raise ValidationError("⚠️ لا توجد خزينة رئيسية معرفة في النظام.")
                
                if treasury.total_balance < self.amount:
                    raise ValidationError(f"⚠️ رصيد الخزينة ({treasury.total_balance}) لا يكفي لصرف مبلغ ({self.amount}).")
                
                treasury.total_balance -= self.amount
                treasury.save()
                
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = "مصروف"
        verbose_name_plural = "المصاريف"

