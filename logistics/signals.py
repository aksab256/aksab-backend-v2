from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.InvoiceItem import InvoiceItem
from .models.mainInventory import InventoryItem

@receiver(post_save, sender=InvoiceItem)
def update_stock_after_sale(sender, instance, created, **kwargs):
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

