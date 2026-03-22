from rest_framework import serializers
from django.db import transaction
from .models.mainInventory import InventoryItem
from .models.transactions import StockTransfer, TransferItem
from .models.products import Product
from .models.customers import Customer # 🆕 استيراد موديل العملاء الجديد

# 1. سيريالايزر الجرد (القديم والمستقر)
class InventoryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_code = serializers.ReadOnlyField(source='product.sku')
    unit = serializers.ReadOnlyField(source='product.unit')

    class Meta:
        model = InventoryItem
        fields = ['id', 'product_name', 'product_code', 'unit', 'stock_quantity', 'last_updated']

# 2. سيريالايزر تفاصيل الأصناف داخل الإذن (الجديد والمعدل)
class TransferItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    unit = serializers.ReadOnlyField(source='product.unit') 
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = TransferItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_image',
            'quantity',
            'unit',
            'unit_at_transfer',
            'is_received'
        ]

    def get_product_image(self, obj):
        if obj.product and obj.product.image:
            return obj.product.image.url
        return None

# 3. سيريالايزر إذن التحويل الكامل (الرأس + الأصناف)
class StockTransferSerializer(serializers.ModelSerializer):
    # نربط الأصناف هنا (Nested Serializer)
    items = TransferItemSerializer(many=True)
    sender_name = serializers.ReadOnlyField(source='sender_warehouse.name')
    receiver_name = serializers.ReadOnlyField(source='receiver_warehouse.name')
    status_display = serializers.ReadOnlyField(source='get_status_display')

    class Meta:
        model = StockTransfer
        fields = [
            'id', 'transfer_no', 'requested_by', 'sender_warehouse', 'sender_name',
            'receiver_warehouse', 'receiver_name', 'status', 'status_display',
            'items', 'created_at'
        ]

    def create(self, validated_data):
        """
        تخصيص عملية الإنشاء لاستقبال الإذن مع أصنافه في وقت واحد
        """
        items_data = validated_data.pop('items') # استخراج قائمة الأصناف

        with transaction.atomic():
            # إنشاء رأس الإذن
            transfer = StockTransfer.objects.create(**validated_data)

            # إنشاء الأصناف التابعة له
            for item_data in items_data:
                TransferItem.objects.create(transfer=transfer, **item_data)

            return transfer

# 4. سيريالايزر المنتجات (المضاف لحل مشكلة الموبايل)
class ProductSerializer(serializers.ModelSerializer):
    """
    هذا السيريالايزر يحول بيانات الأصناف (سمن، فيروز، إلخ)
    لصيغة JSON يفهمها تطبيق الموبايل.
    """
    class Meta:
        model = Product
        fields = '__all__'

# 🆕 5. سيريالايزر العملاء (المحلات) - الجديد كلياً
class CustomerSerializer(serializers.ModelSerializer):
    """
    هذا السيريالايزر مسؤول عن تحويل بيانات العملاء (المحلات)
    بما في ذلك الإحداثيات الجغرافية (Location) لتطبيق المندوب.
    """
    assigned_rep_name = serializers.ReadOnlyField(source='assigned_rep.user.username')

    class Meta:
        model = Customer
        fields = [
            'id', 
            'name', 
            'owner_name', 
            'phone', 
            'address', 
            'latitude', 
            'longitude', 
            'assigned_rep', 
            'assigned_rep_name',
            'is_active', 
            'created_at'
        ]
        # الـ ID والتاريخ والاسم المندوب للقراءة فقط (السيرفر بيحطهم)
        read_only_fields = ['id', 'created_at', 'assigned_rep_name']

