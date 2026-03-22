from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.Invoice import Invoice
from .models.InvoiceItem import InvoiceItem
from .models.mainInventory import InventoryItem
from .models.customers import Customer

@receiver(post_save, sender=InvoiceItem)
def update_stock_after_sale(sender, instance, created, **kwargs):
    """تحديث المخزن (عربة المندوب أو الرئيسي) عند البيع"""
    if created:
        salesman = instance.invoice.salesman
        product = instance.product
        qty_sold = instance.quantity

        stock_record = InventoryItem.objects.filter(
            product=product,
            warehouse__assigned_rep__user=salesman
        ).first()

        if stock_record:
            stock_record.stock_quantity -= qty_sold
            stock_record.save()
            print(f"📦 مخزن: خصم {qty_sold} من عهدة {salesman.username}")
        else:
            main_stock = InventoryItem.objects.filter(
                product=product,
                warehouse__warehouse_type='MAIN'
            ).first()
            if main_stock:
                main_stock.stock_quantity -= qty_sold
                main_stock.save()
                print(f"⚠️ مخزن: تم الخصم من الرئيسي")

@receiver(post_save, sender=Invoice)
def update_customer_financials(sender, instance, created, **kwargs):
    """تحديث مديونية العميل وإجمالي تحصيلاته فور حفظ الفاتورة"""
    if created:
        customer = instance.customer
        
        # 1. زيادة المديونية الحالية بالمبلغ المتبقي
        if instance.remaining_amount > 0:
            customer.current_balance += instance.remaining_amount
            
        # 2. زيادة إجمالي المحصل بالمبلغ المدفوع كاش
        if instance.paid_amount > 0:
            customer.total_paid += instance.paid_amount
            
        customer.save()
        print(f"💰 مالية: العميل {customer.name} | مديونية جديدة: {customer.current_balance} | إجمالي تحصيل: {customer.total_paid}")

