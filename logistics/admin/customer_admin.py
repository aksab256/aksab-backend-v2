from django.contrib import admin
from ..models.customers import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # الحقول اللي تظهر في القائمة الرئيسية (بره)
    list_display = ('name', 'phone', 'assigned_rep', 'current_balance', 'is_active')
    
    # حقول البحث والفلترة
    search_fields = ('name', 'phone', 'owner_name')
    list_filter = ('is_active', 'assigned_rep', 'customer_type', 'created_at')
    
    # تنظيم الحقول داخل صفحة العميل
    fieldsets = (
        ("بيانات الهوية والمحل", {
            'fields': ('name', 'owner_name', 'phone', 'alt_phone', 'customer_type')
        }),
        ("الموقع الجغرافي", {
            'fields': ('address', 'latitude', 'longitude'),
            'classes': ('collapse',), # خليها مخفية وتتفتح بالضغط لو مش محتاجها دايماً
        }),
        ("السياسة المالية وحد الائتمان", {
            'fields': (
                'credit_limit', 
                'credit_days_limit', 
                'current_balance', 
                'total_paid'
            ),
        }),
        ("الإدارة والنشاط", {
            'fields': ('assigned_rep', 'is_active'),
        }),
    )
    
    # حقول للقراءة فقط (عشان المحاسب مغيرش الرصيد يدوي، السيستم هو اللي يحسبه)
    readonly_fields = ('current_balance', 'total_paid')


