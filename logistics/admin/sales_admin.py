from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from ..models.sales_rep import SalesRepresentative
from ..models.sales_manager import SalesManager

class SalesRepInline(admin.StackedInline):
    model = SalesRepresentative
    can_delete = False
    verbose_name_plural = 'إدارة عهدة المندوب'

class SalesManagerInline(admin.StackedInline):
    model = SalesManager
    can_delete = False
    verbose_name_plural = 'إدارة صلاحيات الإدارة'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (SalesRepInline, SalesManagerInline)
    list_display = ('username', 'first_name', 'last_name', 'is_active')

# سيتم تسجيله في الـ __init__
