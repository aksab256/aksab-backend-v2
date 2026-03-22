from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from ..models.transactions import StockTransfer, TransferItem
from ..models.mainInventory import Warehouse  # ✅ أضفنا استيراد المخازن
from ..serializers import StockTransferSerializer

class StockTransferViewSet(viewsets.ModelViewSet):
    """
    الفيو المسؤول عن إدارة طلبات التحميل (Stock Transfers)
    """
    queryset = StockTransfer.objects.all()
    serializer_class = StockTransferSerializer

    def get_queryset(self):
        """تصفية الطلبات بحيث المندوب يشوف طلباته هو بس"""
        queryset = self.queryset
        rep_code = self.request.query_params.get('rep_code')
        status_param = self.request.query_params.get('status')

        if rep_code:
            queryset = queryset.filter(
                Q(requested_by__rep_code=rep_code) |
                Q(receiver_warehouse__assigned_rep__rep_code=rep_code)
            )

        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset.exclude(status='CANCELLED').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """استقبال طلب تحميل جديد من المندوب مع نظام فحص الأخطاء (Debug)"""
        
        # 🟢 رادار 1: طباعة البيانات اللي جاية من الموبايل في الـ Logs
        print(f"📥 Incoming Load Request Data: {request.data}")

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # 1. توليد رقم الطلب تلقائياً لو مش موجود
                    if 'transfer_no' not in serializer.validated_data or not serializer.validated_data['transfer_no']:
                        timestamp = timezone.now().strftime('%y%m%d%H%M%S')
                        serializer.validated_data['transfer_no'] = f"REQ-{timestamp}"

                    # 2. ذكاء اصطناعي بسيط: لو المندوب مبعتش مخزن الإدارة، السيستم يدور عليه
                    if not serializer.validated_data.get('sender_warehouse'):
                        main_wh = Warehouse.objects.filter(warehouse_type='MAIN').first()
                        if main_wh:
                            serializer.validated_data['sender_warehouse'] = main_wh
                            print(f"🏢 Auto-assigned Main Warehouse: {main_wh.name}")

                    # 3. حفظ الطلب
                    self.perform_create(serializer)
                    
                    print("✅ Request saved successfully!")
                    return Response({
                        "status": "success",
                        "message": "تم إرسال طلب التحميل بنجاح",
                        "data": serializer.data
                    }, status=status.HTTP_201_CREATED)

            except Exception as e:
                print(f"❌ Database Error: {str(e)}")
                return Response({
                    "status": "error",
                    "message": f"حدث خطأ أثناء الحفظ: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)

        # 🔴 رادار 2: لو السيريالايزر فشل، هيطبع لنا السبب بالظبط في Koyeb Logs
        print(f"⚠️ Serializer Validation Failed: {serializer.errors}")
        
        return Response({
            "status": "error",
            "message": "بيانات الطلب غير صحيحة",
            "errors": serializer.errors  # بنبعت الأخطاء للموبايل عشان تظهر في الرادار هناك
        }, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

