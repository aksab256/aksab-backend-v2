from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from ..models.transactions import StockTransfer, TransferItem
# تأكد من إنشاء السيريالايزر في ملف serializers.py أو استدعاءه لو وضعته هنا
from ..serializers import StockTransferSerializer 

class StockTransferViewSet(viewsets.ModelViewSet):
    queryset = StockTransfer.objects.all().order_by('-created_at')
    serializer_class = StockTransferSerializer

    def get_queryset(self):
        """تصفية الطلبات بحيث المندوب يشوف طلباته هو بس"""
        queryset = super().get_queryset()
        rep_code = self.request.query_params.get('rep_code')
        status_param = self.request.query_params.get('status')
        
        if rep_code:
            queryset = queryset.filter(requested_by__rep_code=rep_code)
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        return queryset

    def create(self, request, *args, **kwargs):
        """استقبال طلب تحميل جديد (متعدد الأصناف) من المندوب"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # توليد رقم إذن تلقائي لو مش مبعوث
                if 'transfer_no' not in serializer.validated_data:
                    serializer.validated_data['transfer_no'] = f"REQ-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                
                self.perform_create(serializer)
                return Response({
                    "message": "تم إرسال طلب التحميل بنجاح",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

