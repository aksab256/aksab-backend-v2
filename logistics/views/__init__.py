from .auth_views import LoginView
from .work_day_views import WorkDayAPIView

# الفيوهات الخاصة بالمخازن والمنتجات
from .stockView import MyInventoryViewSet, MyTransfersViewSet, ProductViewSet

# الفيوهات الخاصة بطلبات التحميل
from .loadReqest import StockTransferViewSet

# 🆕 إضافة فيو العملاء الجديد
from .customer_views import CustomerViewSet

