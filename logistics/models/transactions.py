from django.db import models, transaction
from django.core.exceptions import ValidationError
from .mainInventory import Warehouse, InventoryItem
from .products import Product
from .sales_rep import SalesRepresentative
from django.utils import timezone

class StockTransfer(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'طلب تحميل (بإنتظار الموافقة)'),
        ('APPROVED', 'تمت الموافقة (قيد التحضير)'),
        ('IN_TRANSIT', 'في الطريق (في عهدة الناقل)'),
        ('COMPLETED', 'تم تأكيد العهدة (استلام كامل)'),
        ('CANCELLED', 'ملغي'),
    ]

    transfer_no = models.CharField(max_length=50, unique=True, verbose_name="رقم الإذن")
    requested_by = models.ForeignKey(SalesRepresentative, on_delete=models.CASCADE, verbose_name="المندوب صاحب الطلب")
    sender_warehouse = models.ForeignKey(Warehouse, related_name='outgoing_transfers', on_delete=models.CASCADE, verbose_name="من مخزن (المصدر)")
    receiver_warehouse = models.ForeignKey(Warehouse, related_name='incoming_transfers', on_delete=models.CASCADE, verbose_name="إلى مخزن (المندوب)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات الطلب")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "إذن تحويل عهدة"
        verbose_name_plural = "أذون تحويل العهد"

    def __str__(self):
        return f"إذن {self.transfer_no} - {self.requested_by.user.username}"

    def save(self, *args, **kwargs):
        # 1. نحفظ الإذن أولاً عشان نضمن وجوده في قاعدة البيانات
        is_new = self.pk is None
        if not is_new:
            old_status = StockTransfer.objects.get(pk=self.pk).status
        else:
            old_status = 'DRAFT'

        super().save(*args, **kwargs)

        # 2. لو الحالة اتغيرت لـ COMPLETED، نفذ حركة المخزن
        if old_status != 'COMPLETED' and self.status == 'COMPLETED':
            with transaction.atomic():
                # بننادي الأصناف بعد الحفظ عشان نضمن إنها موجودة
                for item in self.items.all():
                    # حساب الكمية بالقطع
                    factor = 1
                    if item.selected_unit == 'main':
                        factor = item.product.conversion_factor_main
                    elif item.selected_unit == 'sub':
                        factor = item.product.conversion_factor_sub
                    
                    total_pieces = item.quantity * factor

                    # أ. خصم من مخزن المصدر
                    sender_item, _ = InventoryItem.objects.get_or_create(
                        warehouse=self.sender_warehouse,
                        product=item.product,
                        defaults={'stock_quantity': 0}
                    )
                    
                    if sender_item.stock_quantity < total_pieces:
                        # تنبيه: في الـ Admin يفضل استخدام messages بدل ValidationError هنا
                        sender_item.stock_quantity -= total_pieces # سيسمح بالسالب مؤقتاً لو لم يتم المنع
                    else:
                        sender_item.stock_quantity -= total_pieces
                    sender_item.save()

                    # ب. إضافة لمخزن المندوب
                    receiver_item, _ = InventoryItem.objects.get_or_create(
                        warehouse=self.receiver_warehouse,
                        product=item.product,
                        defaults={'stock_quantity': 0}
                    )
                    receiver_item.stock_quantity += total_pieces
                    receiver_item.save()

                    # تحديث حالة الصنف نفسه
                    item.is_received = True
                    item.received_at = timezone.now()
                    item.save()

class TransferItem(models.Model):
    UNIT_CHOICES = [('main', 'كرتونة'), ('sub', 'دستة/ربطة'), ('base', 'قطعة')]
    transfer = models.ForeignKey(StockTransfer, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="الصنف")
    selected_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='main', verbose_name="الوحدة")
    quantity = models.PositiveIntegerField(verbose_name="الكمية")
    is_received = models.BooleanField(default=False, verbose_name="تم تأكيد استلام الصنف")
    received_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.get_selected_unit_display()}"

