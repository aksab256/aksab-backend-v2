from .auth_views import LoginView
from .auth_views import LoginView
from .work_day_views import WorkDayAPIView

# كده أي ملف بره مجلد views يقدر يستدعيهم مباشرة
from .stockView import MyInventoryViewSet, MyTransfersViewSet
from .loadReqest import StockTransferViewSet 
