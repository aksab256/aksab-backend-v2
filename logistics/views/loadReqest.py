from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from ..models.transactions import StockTransfer, TransferItem
from ..serializers import StockTransferSerializer

class StockTransferViewSet(viewsets.ModelViewSet):
    # إزالة الـ queryset من هنا لمنع التضارب مع get_queryset
    serializer_class = StockTransferSerializer

    def get_queryset(self):
        """
        تصفية الطلبات بحيث المندوب يشوف طلباته هو بس.
        تم تعديلها لتجنب AssertionError وضمان دقة الفلترة.
        """
        # البدء بـ QuerySet نظيف من الموديل مباشرة
        queryset = StockTransfer.objects.all()
        
        rep_code = self.request.query_params.get('rep_code')
        status_param = self.request.query_params.get('status')

        if rep_code:
            # فلترة ذكية: المندوب يرى ما طلبه بنفسه أو ما هو مرسل إليه
            queryset = queryset.filter(
                Q(requested_by__rep_code=rep_code) | 
                Q(receiver_warehouse__assigned_rep__rep_code=rep_code)
            )

        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset.exclude(status='CANCELLED').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """استقبال طلب تحميل جديد (متعدد الأصناف) من المندوب"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # توليد رقم إذن تلقائي لو مش مبعوث (بصيغة احترافية)
                    if 'transfer_no' not in serializer.validated_data or not serializer.validated_data['transfer_no']:
                        timestamp = timezone.now().strftime('%y%m%d%H%M%S')
                        serializer.validated_data['transfer_no'] = f"REQ-{timestamp}"

                    self.perform_create(serializer)
                    
                    return Response({
                        "status": "success",
                        "message": "تم إرسال طلب التحميل بنجاح",
                        "data": serializer.data
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": f"حدث خطأ أثناء الحفظ: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

