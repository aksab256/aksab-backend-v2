from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models.Invoice import Invoice
from .models.InvoiceItem import InvoiceItem
from .models.mainInventory import InventoryItem
from .models.customers import Customer

# 1. سيجنال تحديث المخزن (عند حفظ صنف في الفاتورة)
@receiver(post_save, sender=InvoiceItem)
def update_stock_after_sale(sender, instance, created, **kwargs):
    if created:
        invoice = instance.invoice
        salesman = invoice.salesman
        product = instance.product
        qty_sold = instance.quantity

        # الخصم من مخزن المندوب (السيارة)
        stock_record = InventoryItem.objects.filter(
            product=product,
            warehouse__assigned_rep__user=salesman
        ).first()

        if stock_record:
            stock_record.stock_quantity -= qty_sold
            stock_record.save()
            print(f"✅ مخزن: تم خصم {qty_sold} من عهدة {salesman.username}")
        else:
            # Fallback للمخزن الرئيسي
            main_stock = InventoryItem.objects.filter(
                product=product,
                warehouse__warehouse_type='MAIN'
            ).first()
            if main_stock:
                main_stock.stock_quantity -= qty_sold
                main_stock.save()
                print(f"⚠️ مخزن: تم الخصم من الرئيسي (المندوب ملوش عهدة)")

# 2. سيجنال تحديث مديونية العميل (عند حفظ الفاتورة نفسها)
@receiver(post_save, sender=Invoice)
def update_customer_financials(sender, instance, created, **kwargs):
    if created:
        customer = instance.customer
        # زيادة مديونية العميل بالمبلغ المتبقي (الآجل)
        customer.current_balance += instance.remaining_amount
        
        # لو المندوب حصل مبلغ وهو واقف، نزوده في إجمالي تحصيلات العميل
        if instance.paid_amount > 0:
            customer.total_paid += instance.paid_amount
            
        customer.save()
        print(f"💰 مالية: تم تحديث رصيد العميل {customer.name}. المديونية الحالية: {customer.current_balance}")

