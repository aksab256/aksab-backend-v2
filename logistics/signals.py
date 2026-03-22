from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

# استيراد الموديلات
from .models.InvoiceItem import InvoiceItem
from .models.mainInventory import InventoryItem

@receiver(post_save, sender=InvoiceItem)
def update_stock_after_sale(sender, instance, created, **kwargs):
    if created:  # بننفذ الخصم فقط عند إنشاء السطر لأول مرة
        # بنستخدم transaction.on_commit عشان نتأكد إن الخصم مش هيحصل 
        # إلا لو الفاتورة كلها اتحفظت بنجاح في الداتابيز
        def adjust_inventory():
            product = instance.product
            qty_sold = instance.quantity
            
            # بنحاول نلاقي المنتج في المخزن (InventoryItem)
            # ملحوظة: لو عندك كذا مخزن، لازم نفلتر بمخزن المندوب أو المخزن الرئيسي هنا
            stock_record = InventoryItem.objects.filter(product=product).first()
            
            if stock_record:
                stock_record.quantity -= qty_sold
                stock_record.save()
                print(f"✅ تم خصم {qty_sold} من مخزن {product.name}")
            else:
                print(f"⚠️ تحذير: المنتج {product.name} غير موجود في جدول المخازن!")

        transaction.on_commit(adjust_inventory)

