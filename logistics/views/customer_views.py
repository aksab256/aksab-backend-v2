from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models.customers import Customer
from ..serializers import CustomerSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    """
    إدارة العملاء (المحلات):
    - إضافة محل جديد مع اللوكيشن GPS.
    - عرض قائمة المحلات الخاصة بالمندوب فقط.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        تصفية العملاء:
        المندوب يشوف بس المحلات اللي هو سجلها أو المسؤول عنها.
        """
        user = self.request.user
        # لو المستخدم مربوط بجدول المناديب
        if hasattr(user, 'salesrepresentative'):
            return Customer.objects.filter(assigned_rep=user.salesrepresentative).order_by('-created_at')
        
        # لو أدمن يشوف كل العملاء
        return Customer.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        """
        عند تسجيل عميل جديد:
        يتم ربط العميل تلقائياً بالمندوب اللي فاتح الـ Session حالياً.
        """
        if hasattr(self.request.user, 'salesrepresentative'):
            serializer.save(assigned_rep=self.request.user.salesrepresentative)
            print(f"✅ Customer assigned to Rep: {self.request.user.username}")
        else:
            serializer.save()
            print("⚠️ Customer created without specific Rep (Admin/Staff)")

