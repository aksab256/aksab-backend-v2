from django.db import models, transaction
from django.core.exceptions import ValidationError
from .mainInventory import Warehouse, InventoryItem
from .products import Product
from .sales_rep import SalesRepresentative

class StockTransfer(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'طلب تحميل (بإنتظار الموافقة)'), # يبدأ من المندوب
        ('APPROVED', 'تمت الموافقة (قيد التحضير)'), # موافقة الإدارة
        ('IN_TRANSIT', 'في الطريق (في عهدة الناقل)'), # خرج من المخزن
        ('COMPLETED', 'تم تأكيد العهدة (استلام كامل)'),
        ('CANCELLED', 'ملغي'),
    ]

    transfer_no = models.CharField(max_length=50, unique=True, verbose_name="رقم الإذن")
    
    # المندوب اللي طلب التحميل
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

class TransferItem(models.Model):
    transfer = models.ForeignKey(StockTransfer, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="الصنف")
    
    # الكمية المطلوبة والوحدة من موديل المنتج
    quantity = models.PositiveIntegerField(verbose_name="الكمية")
    unit_at_transfer = models.CharField(max_length=10, verbose_name="الوحدة وقت الطلب") 
    
    # تأكيد استلام الصنف (Checkbox في الفلاتر)
    is_received = models.BooleanField(default=False, verbose_name="تم تأكيد استلام الصنف")
    received_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
