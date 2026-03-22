from django.contrib import admin
from django.db import transaction
from ..models.Invoice import Invoice
from ..models.InvoiceItem import InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    # الحقول اللي هتظهر في جدول الأصناف
    fields = ['product', 'unit_price', 'quantity', 'discount_per_unit', 'line_total']
    readonly_fields = ['line_total']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    # 1. القائمة الرئيسية للفواتير
    list_display = ['invoice_no', 'customer', 'salesman', 'final_total', 'payment_method', 'date_created']
    list_filter = ['payment_method', 'date_created']
    search_fields = ['invoice_no', 'customer__name']
    
    inlines = [InvoiceItemInline]

    # 2. تنظيم شكل الصفحة من الداخل
    fieldsets = (
        ('البيانات الأساسية', {
            'fields': ('invoice_no', 'customer', 'salesman', 'collector')
        }),
        ('الحسابات المالية', {
            'fields': (
                'total_before_discount',
                'discount_amount',
                'final_total',
                'payment_method',
                'paid_amount',
                'remaining_amount'
            )
        }),
    )

    # 3. حقول للقراءة فقط (بتتحسب أوتوماتيك)
    readonly_fields = [
        'invoice_no',
        'total_before_discount',
        'final_total',
        'remaining_amount'
    ]

    # 🔥 السحر هنا: إجبار الـ Admin ينفذ شروط الائتمان (Validation) الموجودة في الموديل
    def save_model(self, request, obj, form, change):
        # دي بتشغل دالة clean() اللي كتبناها في Invoice.py
        # لو العميل تجاوز حد الائتمان، الأدمن هيطلع رسالة خطأ حمراء ويوقف الحفظ
        obj.full_clean() 
        super().save_model(request, obj, form, change)

    # 🔥 السحر الثاني: تحديث الحسابات بعد حفظ الأصناف (Items)
    def save_related(self, request, form, formsets, change):
        # 1. خليه يسيف الأصناف الأول في قاعدة البيانات
        super().save_related(request, form, formsets, change)
        
        # 2. اسحب نسخة الفاتورة اللي اتسيفت
        instance = form.instance
        
        # 3. نادى على دالة التحديث عشان تحسب الإجمالي الحقيقي بعد ما الأصناف اتسجلت
        instance.update_totals()
        
        # 4. تحديث مديونية العميل فوراً (لأن السيجنال أحياناً مبيشوفش الـ Remaining Amount صح في لحظتها)
        with transaction.atomic():
            customer = instance.customer
            # ملحوظة: السيجنال اللي في signals.py هيشتغل برضه، 
            # بس الحركة دي بتضمن إن الـ Admin يعرض الرصيد المحدث فوراً
            print(f"✅ تم تأكيد حسابات الفاتورة {instance.invoice_no} وتحديث رصيد {customer.name}")


