from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ..models.sales_rep import SalesRepresentative
from ..models.sales_manager import SalesManager

# إظهار بيانات المندوب داخل صفحة المستخدم
class SalesRepInline(admin.StackedInline):
    model = SalesRepresentative
    can_delete = False
    verbose_name_plural = 'بيانات المندوب (العهدة والمنطقة)'
    # الحقول التي تظهر للمندوب
    fields = ('employee_code', 'phone', 'region', 'is_active')

# إظهار بيانات المدير داخل صفحة المستخدم
class SalesManagerInline(admin.StackedInline):
    model = SalesManager
    can_delete = False
    verbose_name_plural = 'صلاحيات الإدارة الميدانية'

class CustomUserAdmin(BaseUserAdmin):
    # إضافة Inlines لربط المندوب والمدير بالمستخدم
    inlines = (SalesRepInline, SalesManagerInline)
    
    # تحسين العرض في القائمة الرئيسية للمستخدمين
    list_display = ('username', 'get_full_name', 'get_user_type', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'groups')

    # دالة ذكية لمعرفة نوع المستخدم (مندوب أم مدير) في القائمة
    def get_user_type(self, obj):
        if hasattr(obj, 'sales_rep'):
            return "مندوب مبيعات"
        if hasattr(obj, 'sales_manager'):
            return "مدير مبيعات"
        return "مسؤول نظام"
    get_user_type.short_description = 'نوع الحساب'

# سيتم التسجيل لاحقاً في __init__.py كما ذكرت

