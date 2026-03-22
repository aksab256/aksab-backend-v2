from django.contrib import admin
from ..models.customers import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # الحقول اللي تظهر في الجدول بره
    list_display = ('name', 'phone', 'assigned_rep', 'is_active', 'created_at')
    
    # حقول البحث والفلترة
    search_fields = ('name', 'phone', 'owner_name')
    list_filter = ('is_active', 'assigned_rep', 'created_at')
    
    # تنظيم الحقول جوه صفحة التعديل
    fieldsets = (
        ("بيانات المحل", {
            'fields': ('name', 'owner_name', 'phone')
        }),
        ("الموقع والإحداثيات", {
            'fields': ('address', 'latitude', 'longitude'),
        }),
        ("الإدارة", {
            'fields': ('assigned_rep', 'is_active'),
        }),
    )

