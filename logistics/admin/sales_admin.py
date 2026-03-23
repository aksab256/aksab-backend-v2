from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from ..models.sales_rep import SalesRepresentative
from ..models.sales_manager import SalesManager

# إظهار بيانات المندوب كـ Inline داخل صفحة المستخدم (User)
class SalesRepresentativeInline(admin.StackedInline):
    model = SalesRepresentative
    can_delete = False
    verbose_name_plural = 'بيانات المندوب الفنية'
    fields = ('phone', 'address', 'supervisor', 'insurance_points')
    readonly_fields = ('rep_code',)

# الكلاس الذي يحتاجه ملف __init__
class CustomUserAdmin(UserAdmin):
    inlines = (SalesRepresentativeInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_rep_code')

    def get_rep_code(self, instance):
        try:
            return instance.sales_rep_profile.rep_code
        except:
            return "-"
    get_rep_code.short_description = 'كود المندوب'

@admin.register(SalesRepresentative)
class SalesRepresentativeAdmin(admin.ModelAdmin):
    list_display = ('user', 'rep_code', 'phone', 'supervisor', 'insurance_points')
    search_fields = ('user__username', 'rep_code', 'phone')
    readonly_fields = ('rep_code',)

@admin.register(SalesManager)
class SalesManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)

