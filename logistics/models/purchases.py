import uuid
import datetime
from django.db import models, transaction
from .products import Product
from .mainInventory import Warehouse, InventoryItem

class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم المورد")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    # الرصيد: موجب يعني المورد له فلوس، سالب يعني عليه فلوس
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="رصيد المورد (له)")

    class Meta:
        verbose_name = "مورد"
        verbose_name_plural = "الموردين"

    def __str__(self):
        return f"{self.name} (رصيد: {self.balance})"

class PurchaseInvoice(models.Model):
    invoice_no = models.CharField(max_length=100, unique=True, editable=False, verbose_name="رقم الفاتورة الداخلي")
    supplier_invoice_ref = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم فاتورة المورد (اختياري)")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="المورد")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن المستلم")
    date = models.DateField(auto_now_add=True, verbose_name="تاريخ الاستلام")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="إجمالي الفاتورة")

    class Meta:
        verbose_name = "فاتورة شراء"
        verbose_name_plural = "فواتير الشراء"

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            date_str = datetime.datetime.now().strftime('%Y%m%d')
            unique_id = uuid.uuid4().hex[:4].upper()
            self.invoice_no = f"PUR-{date_str}-{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"فاتورة {self.invoice_no} - {self.supplier.name}"

    def sync_total(self):
        """حساب إجمالي الفاتورة وتحديث رصيد المورد"""
        with transaction.atomic():
            # حساب الإجمالي الجديد من مجموع (سعر الوحدة المختارة * الكمية)
            new_total = sum(item.line_total for item in self.items.all())
            diff = new_total - self.total_amount
            
            PurchaseInvoice.objects.filter(pk=self.pk).update(total_amount=new_total)
            self.total_amount = new_total
            
            # تحديث رصيد المورد
            self.supplier.balance += diff
            self.supplier.save()

class PurchaseItem(models.Model):
    UNIT_CHOICES = [
        ('main', 'وحدة كبرى (كرتونة)'),
        ('sub', 'وحدة متوسطة (دستة/ربطة)'),
        ('base', 'وحدة صغرى (قطعة)'),
    ]

    invoice = models.ForeignKey(PurchaseInvoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="الصنف")
    
    # 🆕 المنسدلة الموحدة
    selected_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='main', verbose_name="وحدة الشراء")
    
    quantity = models.PositiveIntegerField(verbose_name="الكمية")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر شراء الوحدة")
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # 1. حساب إجمالي السطر المالي
            self.line_total = self.quantity * self.cost_price

            # 2. تحديد معامل التحويل للمخزن
            factor = self.product.conversion_factor_main if self.selected_unit == 'main' else \
                     self.product.conversion_factor_sub if self.selected_unit == 'sub' else 1
            
            total_pieces = self.quantity * factor

            # 3. تحديث المخزن (زيادة الرصيد)
            inventory, created = InventoryItem.objects.get_or_create(
                warehouse=self.invoice.warehouse,
                product=self.product,
                defaults={'stock_quantity': 0}
            )

            # لو تعديل: نطرح الكمية القديمة بالمعامل القديم قبل إضافة الجديد
            if self.pk:
                old_item = PurchaseItem.objects.get(pk=self.pk)
                old_factor = self.product.conversion_factor_main if old_item.selected_unit == 'main' else \
                             self.product.conversion_factor_sub if old_item.selected_unit == 'sub' else 1
                inventory.stock_quantity -= (old_item.quantity * old_factor)

            inventory.stock_quantity += total_pieces
            inventory.save()

            super().save(*args, **kwargs)
            self.invoice.sync_total()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            factor = self.product.conversion_factor_main if self.selected_unit == 'main' else \
                     self.product.conversion_factor_sub if self.selected_unit == 'sub' else 1
            
            inventory = InventoryItem.objects.filter(warehouse=self.invoice.warehouse, product=self.product).first()
            if inventory:
                inventory.stock_quantity -= (self.quantity * factor)
                inventory.save()

            invoice = self.invoice
            super().delete(*args, **kwargs)
            invoice.sync_total()

class SupplierPayment(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payments', verbose_name="المورد")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="المبلغ المدفوع")
    date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الدفع")
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم الإيصال / مرجع")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                self.supplier.balance -= self.amount
                self.supplier.save()
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = "سداد مورد"
        verbose_name_plural = "سدادات الموردين"

