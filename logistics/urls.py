from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.auth_views import LoginView, create_admin
from .views.work_day_views import WorkDayAPIView
# استيراد الفيو الجديد ProductViewSet من ملف stockView
from .views.stockView import MyInventoryViewSet, MyTransfersViewSet, ProductViewSet
from .views.loadReqest import StockTransferViewSet

# إعداد الـ Router
router = DefaultRouter()

# 1. عرض جرد عهدة المندوب (السيارة)
router.register(r'my-inventory', MyInventoryViewSet, basename='my-inventory')

# 2. عرض التحويلات المعلقة الواردة للمندوب لتأكيدها
router.register(r'my-transfers', MyTransfersViewSet, basename='my-transfers')

# 3. إدارة طلبات التحميل (إنشاء طلب جديد / عرض الطلبات السابقة)
router.register(r'stock-transfers', StockTransferViewSet, basename='stock-transfer')

# 4. ✅ الرابط السحري: عرض قائمة الأصناف (سمن، فيروز، إلخ) للموبايل
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    # 1. روابط الـ Router (المخازن والتحويلات والمنتجات)
    path('', include(router.urls)),

    # 2. روابط الـ Auth واليومية
    path('login/', LoginView.as_view(), name='login'),
    path('work-day/', WorkDayAPIView.as_view(), name='work_day_api'),

    # 3. رابط إنشاء الأدمن (للطوارئ)
    path('create-admin/', create_admin),
]

