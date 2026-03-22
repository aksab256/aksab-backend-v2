from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models.InvoiceItem import InvoiceItem
from .models.mainInventory import InventoryItem

@receiver(post_save, sender=InvoiceItem)
def update_stock_after_sale(sender, instance, created, **kwargs):
    if created:
        def adjust_inventory():
            product = instance.product
            qty_sold = instance.quantity
            
            # البحث عن المنتج في المخزن (InventoryItem)
            # ملحوظة: لو عندك كذا مخزن، يفضل فلترة المخزن المرتبط بالمندوب هنا
            stock_record = InventoryItem.objects.filter(product=product).first()
            
            if stock_record:
                # ✅ التصحيح: الحقل اسمه stock_quantity كما في الموديل
                stock_record.stock_quantity -= qty_sold
                stock_record.save()
                print(f"✅ تم خصم {qty_sold} من {product.name}. المتبقي: {stock_record.stock_quantity}")
            else:
                print(f"⚠️ تحذير: المنتج {product.name} غير متوفر في أي مخزن!")

        transaction.on_commit(adjust_inventory)

