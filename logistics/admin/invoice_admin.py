from django.contrib import admin, messages
from django.db import transaction
from ..models.Invoice import Invoice
from ..models.InvoiceItem import InvoiceItem
from ..models.payments import Collection  # ✅ الاستدعاء الصحيح من ملف payments
from django.core.exceptions import ValidationError

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    fields = ['product', 'unit_price', 'quantity', 'discount_per_unit', 'line_total']
    readonly_fields = ['line_total']

class CollectionInline(admin.TabularInline):
    """عرض التحصيلات اللي تمت على الفاتورة دي"""
    model = Collection
    extra = 0
    fields = ['collection_date', 'amount', 'collector', 'notes']
    readonly_fields = ['collection_date', 'amount', 'collector', 'notes']
    can_delete = False  # أمان عشان مفيش تحصيل يتمسح بالخطأ

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    # ✅ السطر المطلوب لحل مشكلة الـ autocomplete_fields
    search_fields = ['invoice_no', 'customer__name'] 

    list_display = ['invoice_no', 'customer', 'salesman', 'final_total', 'payment_method', 'date_created']
    
    # أضفنا الـ fields هنا عشان نضمن ظهور المربعات المالية
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
    
    readonly_fields = ['invoice_no', 'total_before_discount', 'final_total', 'remaining_amount']
    
    # ربط الأصناف والتحصيلات في نفس شاشة الفاتورة
    inlines = [InvoiceItemInline, CollectionInline]

    def save_related(self, request, form, formsets, change):
        """حفظ الأصناف والتحقق من المديونية في عملية واحدة آمنة"""
        try:
            with transaction.atomic():
                # حفظ الأصناف (Items)
                super().save_related(request, form, formsets, change)
                
                # استدعاء المحرك الرئيسي لحساب المبالغ وتحديث رصيد العميل
                instance = form.instance
                instance.update_totals()
                
        except ValidationError as e:
            # إظهار رسالة الخطأ الحمراء في الأدمن
            messages.error(request, str(e))
            # لو الفاتورة لسه جديدة وفشلت في الائتمان، بنمسح الهيكل عشان متبوظش الأرقام
            if not change:
                form.instance.delete()

