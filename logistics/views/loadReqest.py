from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from ..models.transactions import StockTransfer, TransferItem
from ..models.mainInventory import Warehouse, SalesRepresentative # أضفنا السيلز ريب
from ..serializers import StockTransferSerializer

class StockTransferViewSet(viewsets.ModelViewSet):
    queryset = StockTransfer.objects.all()
    serializer_class = StockTransferSerializer

    def create(self, request, *args, **kwargs):
        print(f"📥 Incoming Data: {request.data}")
        
        data = request.data.copy() # نسخة قابلة للتعديل

        # 1️⃣ حل مشكلة transfer_no: نولده هنا قبل السيريالايزر
        if not data.get('transfer_no'):
            timestamp = timezone.now().strftime('%y%m%d%H%M%S')
            data['transfer_no'] = f"REQ-{timestamp}"

        # 2️⃣ حل مشكلة requested_by: لو المبعوت User ID (زي 3)، نحوله لـ Rep ID
        try:
            rep_id = data.get('requested_by')
            # لو مش لاقي مندوب بالأيدي ده، ندور بالمستخدم اللي باعت الطلب
            if not SalesRepresentative.objects.filter(id=rep_id).exists():
                rep = SalesRepresentative.objects.filter(user_id=request.user.id).first()
                if rep:
                    data['requested_by'] = rep.id
                    print(f"🔄 Fixed requested_by: changed to Rep ID {rep.id}")
        except:
            pass

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # إسناد مخزن الشركة تلقائياً لو مش موجود
                    if not serializer.validated_data.get('sender_warehouse'):
                        main_wh = Warehouse.objects.filter(warehouse_type='MAIN').first()
                        if main_wh:
                            serializer.validated_data['sender_warehouse'] = main_wh

                    self.perform_create(serializer)
                    print("✅ Saved Successfully!")
                    return Response({
                        "status": "success",
                        "message": "تم إرسال طلب التحميل بنجاح",
                        "data": serializer.data
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"❌ DB Error: {str(e)}")
                return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"⚠️ Serializer Errors: {serializer.errors}")
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

