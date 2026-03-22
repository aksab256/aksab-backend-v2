from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.auth_views import LoginView, create_admin
from .views.work_day_views import WorkDayAPIView

# 1. استيراد فيوهات المخازن والمنتجات من الملف القديم
from .views.stockView import (
    MyInventoryViewSet, 
    MyTransfersViewSet, 
    ProductViewSet
)

# 2. استيراد فيو طلبات التحميل
from .views.loadReqest import StockTransferViewSet

# 3. 🆕 استيراد فيو العملاء من ملفه الجديد والمنفصل
from .views.customer_views import CustomerViewSet 

# إعداد الـ Router
router = DefaultRouter()

# 1. عرض جرد عهدة المندوب (السيارة)
router.register(r'my-inventory', MyInventoryViewSet, basename='my-inventory')

# 2. عرض التحويلات المعلقة الواردة للمندوب لتأكيدها
router.register(r'my-transfers', MyTransfersViewSet, basename='my-transfers')

# 3. إدارة طلبات التحميل (إنشاء طلب جديد / عرض الطلبات السابقة)
router.register(r'stock-transfers', StockTransferViewSet, basename='stock-transfer')

# 4. عرض قائمة الأصناف (سمن، فيروز، إلخ) للموبايل
router.register(r'products', ProductViewSet, basename='product')

# 5. إدارة العملاء (تسجيل محل جديد / عرض قائمة المحلات)
router.register(r'customers', CustomerViewSet, basename='customer')

urlpatterns = [
    # 1. روابط الـ Router (المخازن، التحويلات، المنتجات، والعملاء)
    path('', include(router.urls)),

    # 2. روابط الـ Auth واليومية
    path('login/', LoginView.as_view(), name='login'),
    path('work-day/', WorkDayAPIView.as_view(), name='work_day_api'),

    # 3. رابط إنشاء الأدمن (للطوارئ)
    path('create-admin/', create_admin),
]

