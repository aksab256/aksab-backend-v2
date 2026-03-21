from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.auth_views import LoginView, create_admin
from .views.work_day_views import WorkDayAPIView
from .views import MyInventoryViewSet, MyTransfersViewSet, StockTransferViewSet

router = DefaultRouter()

router.register(r'my-inventory', MyInventoryViewSet, basename='my-inventory')
router.register(r'my-transfers', MyTransfersViewSet, basename='my-transfers')
router.register(r'stock-transfers', StockTransferViewSet, basename='stock-transfer')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('work-day/', WorkDayAPIView.as_view(), name='work_day_api'),

    # 👇 ضيف هنا مش تعمل واحدة جديدة
    path('create-admin/', create_admin),

    path('', include(router.urls)),
]
