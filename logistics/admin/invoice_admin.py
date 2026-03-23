from django.contrib import admin, messages
from django.db import transaction
from ..models.Invoice import Invoice
from ..models.InvoiceItem import InvoiceItem
# تأكد من استيراد الموديلات الصحيحة للتحصيل لو موجودة في ملف منفصل
# from ..models.payments import Collection 

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1 # خليناها 1 عشان يفتح سطر جديد جاهز للإضافة
    
    # 🆕 التعديل الجوهري: إضافة selected_unit في الترتيب الصحيح
    fields = ['product', 'selected_unit', 'unit_price', 'quantity', 'discount_per_unit', 'line_total']
    
    # جعل الإجمالي للقراءة فقط عشان السيستم يحسبه
    readonly_fields = ['line_total']
    
    # تحسين اختيار المنتج (Dropdown مع بحث)
    autocomplete_fields = ['product'] 

class InvoiceAdmin(admin.ModelAdmin):
    search_fields = ['invoice_no', 'customer__name']
    list_display = [
        'invoice_no', 'customer', 'warehouse', 'salesman', 
        'final_total', 'payment_method', 'date_created'
    ]
    list_filter = ['warehouse', 'payment_method', 'date_created', 'salesman']
    
    fieldsets = (
        ('بيانات الفاتورة الأساسية', {
            'fields': (('invoice_no', 'date_created'), ('customer', 'warehouse'), ('salesman', 'collector'))
        }),
        ('الحسابات المالية (تحديث تلقائي)', {
            'fields': (
                ('total_before_discount', 'discount_amount'),
                ('final_total', 'payment_method'),
                ('paid_amount', 'remaining_amount')
            )
        }),
    )

    # الحقول اللي بتتحسب أوتوماتيك يفضل تكون Readonly في الأدمن الرئيسي
    readonly_fields = ['invoice_no', 'date_created', 'total_before_discount', 'final_total', 'remaining_amount']
    
    inlines = [InvoiceItemInline] # يمكنك إضافة CollectionInline هنا أيضاً

    def save_related(self, request, form, formsets, change):
        """تأمين عملية الخصم من المخزن وتحديث الأرصدة"""
        try:
            with transaction.atomic():
                # 1. حفظ الأصناف (ده بيشغل الـ save بتاع InvoiceItem اللي بيخصم من المخزن)
                super().save_related(request, form, formsets, change)
                
                # 2. إعادة حساب الإجماليات النهائية للفاتورة
                instance = form.instance
                instance.update_totals()
                
        except Exception as e:
            # عرض أي خطأ (زي عجز المخزن) كرسالة حمراء في الأدمن
            messages.error(request, f"⚠️ خطأ في الحفظ: {str(e)}")
            # لو الفاتورة جديدة وفشلت، لا نريد ترك "رأس فاتورة" فارغ بدون أصناف
            if not change and instance.pk:
                instance.delete()

# تسجيل الموديل
admin.site.register(Invoice, InvoiceAdmin)

