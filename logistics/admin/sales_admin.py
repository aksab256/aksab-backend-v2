from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from ..models.sales_rep import SalesRepresentative
from ..models.sales_manager import SalesManager

# إعداد ظهور المندوب كـ Inline جوه صفحة المستخدم (User)
class SalesRepresentativeInline(admin.StackedInline):
    model = SalesRepresentative
    can_delete = False
    verbose_name_plural = 'بيانات المندوب'
    # عرض الحقول المتاحة فقط في الموديل الحالي
    fields = ('warehouse', 'target_amount') 

class CustomUserAdmin(UserAdmin):
    inlines = (SalesRepresentativeInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_region')
    
    def get_region(self, instance):
        # بنحاول نجيب المنطقة لو المندوب مربوط، وإلا نرجع فاضي
        try:
            return instance.salesrepresentative.warehouse.name
        except:
            return "-"
    get_region.short_description = 'المخزن/الفرع'

# تسجيل الأدمن للمناديب بشكل مستقل برضه لو حبيت
@admin.register(SalesRepresentative)
class SalesRepresentativeAdmin(admin.ModelAdmin):
    list_display = ('user', 'warehouse', 'target_amount')
    search_fields = ('user__username', 'warehouse__name')

