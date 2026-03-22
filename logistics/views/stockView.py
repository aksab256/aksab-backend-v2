from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Q  # ✅ ضروري جداً للفلترة المتقدمة

# استيراد الموديلات
from ..models.mainInventory import InventoryItem
from ..models.transactions import StockTransfer
from ..models.products import Product  # ✅ أضفنا استيراد موديل المنتجات

# استيراد السيريالايزر
from ..serializers import (
    InventoryItemSerializer, 
    StockTransferSerializer, 
    ProductSerializer  # ✅ تأكد من وجوده في serializers.py
)

class MyInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    يعرض للمندوب البضاعة الموجودة في عهدته (سيارته) حالياً.
    """
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        rep_code = self.request.query_params.get('rep_code')

        if rep_code:
            return InventoryItem.objects.filter(
                warehouse__assigned_rep__rep_code=rep_code
            )
        
        return InventoryItem.objects.filter(
            warehouse__assigned_rep__user=user
        )

class MyTransfersViewSet(viewsets.ModelViewSet):
    """
    يعرض "تحويلات العهد" المرسلة للمندوب ليقوم بتأكيد استلامها.
    """
    queryset = StockTransfer.objects.all()
    serializer_class = StockTransferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        rep_code = self.request.query_params.get('rep_code')
        queryset = self.queryset

        if rep_code:
            queryset = queryset.filter(
                Q(receiver_warehouse__assigned_rep__rep_code=rep_code) |
                Q(requested_by__rep_code=rep_code)
            )
        else:
            queryset = queryset.filter(
                Q(receiver_warehouse__assigned_rep__user=user) |
                Q(requested_by__user=user)
            )

        return queryset.exclude(status='CANCELLED').order_by('-created_at')

    def update(self, request, *args, **kwargs):
        """تأكيد استلام العهدة"""
        instance = self.get_object()

        if instance.status != 'IN_TRANSIT':
            return Response(
                {'error': 'عفواً، لا يمكن تأكيد استلام عهدة ليست في الطريق (In Transit) حالياً.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        requested_status = request.data.get('status')
        if requested_status == 'COMPLETED':
            try:
                instance.status = 'COMPLETED'
                instance.save()
                return Response({
                    'message': 'تأكيد العهدة: تم استلام الأمانات بنجاح، وتحديث الأرصدة المخزنية.',
                    'transfer_no': instance.transfer_no,
                    'status': instance.status
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {'error': 'غير مسموح بتعديل بيانات العهدة الأصلية. يمكنك فقط تأكيد الاستلام.'},
            status=status.HTTP_403_FORBIDDEN
        )

# --- 🆕 الجزء الجديد المضاف لحل مشكلة الموبايل ---

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    هذا الفيو يسمح للمندوب برؤية قائمة المنتجات (سمن، فيروز، إلخ) 
    ليتمكن من اختيارها في طلب التحميل الجديد.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated] # ✅ يسمح للمندوب بالوصول للمنتجات

