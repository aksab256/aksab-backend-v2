from django.contrib import admin
from ..models.customers import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # 1. القائمة المختصرة (الشاشة الرئيسية للعملاء)
    list_display = (
        'name', 
        'phone', 
        'assigned_rep', 
        'current_balance',  # تظهر بره للمراقبة السريعة
        'is_active'
    )
    
    # 2. أدوات البحث والفلترة
    search_fields = ('name', 'phone', 'owner_name')
    list_filter = ('is_active', 'assigned_rep', 'customer_type', 'created_at')
    
    # 3. تنظيم البيانات داخل الصفحة (Layout)
    fieldsets = (
        ("بيانات الهوية والمحل", {
            'fields': (
                'name', 
                'owner_name', 
                'phone', 
                'alt_phone', 
                'customer_type'
            )
        }),
        ("الموقع الجغرافي", {
            'fields': ('address', 'latitude', 'longitude'),
            'classes': ('collapse',), # مخفية بشكل افتراضي لتوفير المساحة
        }),
        ("السياسة المالية (تعديل الإدارة)", {
            'description': "هذه الحقول تحدد سقف التعامل مع العميل",
            'fields': (
                'credit_limit',      # قابل للتعديل (الحد النقدي)
                'credit_days_limit', # قابل للتعديل (الحد الزمني)
            ),
        }),
        ("الأرصدة الحالية (تحديث تلقائي)", {
            'description': "قيم محسوبة من واقع الفواتير والتحصيلات - لا يمكن تعديلها يدوياً",
            'fields': (
                'current_balance',   # Read-only
                'total_paid'         # Read-only
            ),
        }),
        ("الإدارة والنشاط", {
            'fields': ('assigned_rep', 'is_active'),
        }),
    )
    
    # 4. منع التعديل اليدوي على الأرصدة لضمان سلامة الحسابات
    readonly_fields = ('current_balance', 'total_paid')

    # ملاحظة هندسية: ديجانجو بيسمح لك من خلال الـ Group Permissions 
    # إنك تدي "المحاسب" صلاحية Change للعميل فيقدر يغير الـ Limits،
    # وتدي "المراقب" صلاحية View فقط فيشوف كل حاجة من غير ما يقدر يلمس سهم.

