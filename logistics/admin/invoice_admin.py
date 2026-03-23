from django.contrib import admin, messages
from django.db import transaction
from ..models.Invoice import Invoice
from ..models.InvoiceItem import InvoiceItem
from ..models.payments import Collection
from django.core.exceptions import ValidationError

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    # تأكدنا من ترتيب الحقول ومتابعة الـ line_total
    fields = ['product', 'unit_price', 'quantity', 'discount_per_unit', 'line_total']
    readonly_fields = ['line_total']

class CollectionInline(admin.TabularInline):
    """عرض التحصيلات اللي تمت على الفاتورة دي"""
    model = Collection
    extra = 0
    fields = ['collection_date', 'amount', 'collector', 'notes']
    readonly_fields = ['collection_date', 'amount', 'collector', 'notes']
    can_delete = False 

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    search_fields = ['invoice_no', 'customer__name']
    list_display = ['invoice_no', 'customer', 'warehouse', 'salesman', 'final_total', 'payment_method', 'date_created']
    list_filter = ['warehouse', 'payment_method', 'date_created'] # أضفنا فلتر بالمخزن لسهولة البحث

    # تحديث الـ fieldsets لإظهار خانة المخزن الجديدة
    fieldsets = (
        ('البيانات الأساسية', {
            'fields': ('invoice_no', 'customer', 'warehouse', 'salesman', 'collector') # ⬅️ أضفنا warehouse هنا
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
    
    inlines = [InvoiceItemInline, CollectionInline]

    def save_related(self, request, form, formsets, change):
        """حفظ الأصناف والتحقق من المديونية والمخزن في عملية واحدة آمنة"""
        try:
            with transaction.atomic():
                # 1. حفظ الأصناف أولاً (عشان دالة الـ save في InvoiceItem تخصم من المخزن)
                super().save_related(request, form, formsets, change)
                
                # 2. تحديث إجماليات الفاتورة ورصيد العميل
                instance = form.instance
                instance.update_totals()
                
        except ValidationError as e:
            # إظهار رسالة الخطأ (مثلاً: عجز في المخزن أو تجاوز حد الائتمان)
            messages.error(request, str(e))
            if not change:
                # لو الفاتورة جديدة وفشلت، بنلغي العملية تماماً
                form.instance.delete()

