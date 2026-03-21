from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Q  # ✅ ضروري جداً للفلترة المتقدمة
from ..models.mainInventory import InventoryItem
from ..models.transactions import StockTransfer
from ..serializers import InventoryItemSerializer, StockTransferSerializer

class MyInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    يعرض للمندوب البضاعة الموجودة في عهدته (سيارته) حالياً.
    تم تعديله ليكون أكثر مرونة في الفلترة لضمان ظهور البيانات.
    """
    queryset = InventoryItem.objects.all() # ✅ صمام أمان لمنع AssertionError
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        rep_code = self.request.query_params.get('rep_code')

        # الفلترة الأساسية بناءً على المندوب المربوط بالمخزن
        if rep_code:
            # تم إزالة شرط 'VAN' مؤقتاً لضمان ظهور البيانات أياً كان مسمى نوع المخزن
            return InventoryItem.objects.filter(
                warehouse__assigned_rep__rep_code=rep_code
            )
        
        # الفلترة بالمستخدم المسجل حالياً
        return InventoryItem.objects.filter(
            warehouse__assigned_rep__user=user
        )

class MyTransfersViewSet(viewsets.ModelViewSet):
    """
    يعرض "تحويلات العهد" المرسلة للمندوب ليقوم بتأكيد استلامها.
    تسمح للمندوب برؤية الشحنات (العهد المعلقة) التي في الطريق (IN_TRANSIT).
    """
    queryset = StockTransfer.objects.all() # ✅ صمام أمان لمنع AssertionError
    serializer_class = StockTransferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        تعديل جلب البيانات ليكون أكثر استقراراً ويمنع خطأ الـ 500 (AssertionError).
        """
        user = self.request.user
        rep_code = self.request.query_params.get('rep_code')

        # ✅ البدء من الكويري سيت المعرف أعلاه
        queryset = self.queryset

        # فلترة التحويلات بناءً على المندوب (كمستلم للأمانات أو كطالب للعهدة)
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

        # استبعاد التحويلات الملغية وعرض الأحدث أولاً
        return queryset.exclude(status='CANCELLED').order_by('-created_at')

    def update(self, request, *args, **kwargs):
        """
        تخصيص عملية التحديث (تأكيد العهدة):
        1. التحقق من أن الحالة الحالية للطلب هي 'IN_TRANSIT'.
        2. تحديث الحالة فقط إلى 'COMPLETED' لتشغيل منطق الـ save في الموديل.
        3. منع تعديل أي حقول أخرى (الكمية، الصنف، المخازن).
        """
        instance = self.get_object()

        # 🛡️ صمام أمان 1: لا يمكن استلام طلب إلا لو كان في الطريق
        if instance.status != 'IN_TRANSIT':
            return Response(
                {'error': 'عفواً، لا يمكن تأكيد استلام عهدة ليست في الطريق (In Transit) حالياً.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🛡️ صمام أمان 2: التأكد أن المندوب يرسل طلب إغلاق العهدة فقط
        requested_status = request.data.get('status')
        if requested_status == 'COMPLETED':
            try:
                # تحديث حقل الحالة فقط
                instance.status = 'COMPLETED'
                # حفظ الـ instance سيؤدي لتشغيل منطق الخصم والإضافة في الموديل أوتوماتيكياً
                instance.save()

                return Response({
                    'message': 'تأكيد العهدة: تم استلام الأمانات بنجاح، وتحديث الأرصدة المخزنية.',
                    'transfer_no': instance.transfer_no,
                    'status': instance.status
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 🛡️ صمام أمان 3: منع أي محاولة لتعديل بيانات أخرى (مثل الكمية أو الصنف)
        return Response(
            {'error': 'غير مسموح بتعديل بيانات العهدة الأصلية. يمكنك فقط تأكيد الاستلام.'},
            status=status.HTTP_403_FORBIDDEN
        )

