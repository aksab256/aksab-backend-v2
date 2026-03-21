from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.auth_views import LoginView, create_admin # دمجناهم هنا
from .views.work_day_views import WorkDayAPIView
from .views import MyInventoryViewSet, MyTransfersViewSet, StockTransferViewSet

# إعداد الـ Router
router = DefaultRouter()
router.register(r'my-inventory', MyInventoryViewSet, basename='my-inventory')
router.register(r'my-transfers', MyTransfersViewSet, basename='my-transfers')
router.register(r'stock-transfers', StockTransferViewSet, basename='stock-transfer')

urlpatterns = [
    # 1. روابط الـ Router (المخازن والتحويلات)
    path('', include(router.urls)),
    
    # 2. روابط الـ Auth واليومية
    path('login/', LoginView.as_view(), name='login'),
    path('work-day/', WorkDayAPIView.as_view(), name='work_day_api'),
    
    # 3. رابط إنشاء الأدمن (للطوارئ)
    path('create-admin/', create_admin),
]

