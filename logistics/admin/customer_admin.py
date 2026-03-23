from django.contrib import admin
from ..models.customers import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'assigned_rep', 'current_balance', 'is_active')
    search_fields = ('name', 'phone', 'owner_name')
    list_filter = ('is_active', 'assigned_rep', 'customer_type', 'created_at')
    readonly_fields = ('current_balance', 'total_paid')

    fieldsets = (
        ("بيانات الهوية والمحل", {
            'fields': ('name', 'owner_name', 'phone', 'alt_phone', 'customer_type')
        }),
        ("الموقع الجغرافي", {
            'fields': ('address', 'latitude', 'longitude'),
            'classes': ('collapse',),
        }),
        ("السياسة المالية", {
            'fields': ('credit_limit', 'credit_days_limit'),
        }),
        ("الأرصدة الحالية", {
            'fields': ('current_balance', 'total_paid'),
        }),
        ("الإدارة والنشاط", {
            'fields': ('assigned_rep', 'is_active'),
        }),
    )

