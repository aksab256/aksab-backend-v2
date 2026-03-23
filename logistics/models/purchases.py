import uuid
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
    # توليد رقم الفاتورة أوتوماتيكياً (مثال: PUR-20231025-ABCD)
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
        # توليد رقم فاتورة تلقائي لو مش موجود
        if not self.invoice_no:
            import datetime
            date_str = datetime.datetime.now().strftime('%Y%m%d')
            unique_id = uuid.uuid4().hex[:4].upper()
            self.invoice_no = f"PUR-{date_str}-{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"فاتورة {self.invoice_no} - {self.supplier.name}"

    def sync_total(self):
        """حساب إجمالي الفاتورة وتحديث رصيد المورد"""
        with transaction.atomic():
            # 1. احسب الإجمالي الجديد من الأصناف
            new_total = sum(item.quantity_in_main_unit * item.cost_price_per_main_unit for item in self.items.all())
            
            # 2. الفرق بين الإجمالي القديم والجديد عشان نحدث رصيد المورد بدقة
            diff = new_total - self.total_amount
            
            # 3. تحديث الفاتورة
            PurchaseInvoice.objects.filter(pk=self.pk).update(total_amount=new_total)
            
            # 4. تحديث رصيد المورد (زيادة مديونية)
            self.supplier.balance += diff
            self.supplier.save()

class PurchaseItem(models.Model):
    invoice = models.ForeignKey(PurchaseInvoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity_in_main_unit = models.PositiveIntegerField(verbose_name="الكمية (بالكرتونة)")
    cost_price_per_main_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر شراء الكرتونة")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # 1. تحديث المخزن (تحويل كراتين لقطع)
            total_pieces = self.quantity_in_main_unit * self.product.conversion_factor_main
            inventory, created = InventoryItem.objects.get_or_create(
                warehouse=self.invoice.warehouse,
                product=self.product
            )
            
            # لو تعديل (نطرح القديم ونزود الجديد)
            if self.pk:
                old_item = PurchaseItem.objects.get(pk=self.pk)
                old_pieces = old_item.quantity_in_main_unit * old_item.product.conversion_factor_main
                inventory.stock_quantity -= old_pieces

            inventory.stock_quantity += total_pieces
            inventory.save()

            # 2. حفظ سجل الصنف
            super().save(*args, **kwargs)

            # 3. تحديث إجمالي الفاتورة ورصيد المورد
            self.invoice.sync_total()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            # طرح الكمية من المخزن عند مسح الصنف
            total_pieces = self.quantity_in_main_unit * self.product.conversion_factor_main
            inventory = InventoryItem.objects.filter(warehouse=self.invoice.warehouse, product=self.product).first()
            if inventory:
                inventory.stock_quantity -= total_pieces
                inventory.save()
            
            # تحديث رصيد المورد (طرح قيمة الصنف الممسوح)
            amount_to_subtract = self.quantity_in_main_unit * self.cost_price_per_main_unit
            self.invoice.supplier.balance -= amount_to_subtract
            self.invoice.supplier.save()

            invoice = self.invoice
            super().delete(*args, **kwargs)
            # تحديث إجمالي الفاتورة المسجل
            invoice.sync_total()

# موديل جديد للمدفوعات (عشان لما تدفع فلوس للمورد رصيده يقل)
class SupplierPayment(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payments', verbose_name="المورد")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="المبلغ المدفوع")
    date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الدفع")
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم الإيصال / مرجع")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk: # عند الإنشاء فقط
                self.supplier.balance -= self.amount
                self.supplier.save()
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = "سداد مورد"
        verbose_name_plural = "سدادات الموردين"

