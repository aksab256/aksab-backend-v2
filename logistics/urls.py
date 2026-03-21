from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.auth_views import LoginView
from .views.work_day_views import WorkDayAPIView
# استيراد الـ ViewSets من الـ __init__ اللي جهزناه
from .views import MyInventoryViewSet, MyTransfersViewSet, StockTransferViewSet

# إعداد الـ Router للـ ViewSets
router = DefaultRouter()

# 1. جرد عهدة السيارة الحالي
router.register(r'my-inventory', MyInventoryViewSet, basename='my-inventory')

# 2. عرض التحويلات (القديم - صنف واحد - للتوافق مع النسخ الحالية لو لزم الأمر)
router.register(r'my-transfers', MyTransfersViewSet, basename='my-transfers')

# 3. نظام طلبات التحميل الجديد (الأصناف المتعددة + الاستلام بـ Checkbox)
# المسار ده اللي المندوب هيستخدمه لبعت طلب تحميل (POST) أو رؤية أصناف الإذن (GET)
router.register(r'stock-transfers', StockTransferViewSet, basename='stock-transfer')

urlpatterns = [
    # روابط الـ Auth والـ WorkDay
    path('login/', LoginView.as_view(), name='login'),
    path('work-day/', WorkDayAPIView.as_view(), name='work_day_api'),

    # دمج روابط الـ Router تلقائياً (المخازن، التحويلات، طلبات التحميل)
    path('', include(router.urls)),
]

