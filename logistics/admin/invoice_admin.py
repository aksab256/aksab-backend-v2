from django.contrib import admin
from ..models.Invoice import Invoice
from ..models.InvoiceItem import InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    # عرض الحقول المتاحة فقط في InvoiceItem
    fields = ['product', 'unit_price', 'quantity', 'discount_per_unit', 'line_total']
    readonly_fields = ['line_total']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    # الحقول اللي هتظهر في القائمة الرئيسية
    list_display = ['invoice_no', 'customer', 'salesman', 'final_total', 'payment_method', 'date_created']
    list_filter = ['payment_method', 'date_created']
    search_fields = ['invoice_no', 'customer__name']
    
    inlines = [InvoiceItemInline]
    
    # الحقول المتاحة فقط في موديل Invoice الحالي
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
    
    # حقول للقراءة فقط لأنها بتتحسب أوتوماتيك من الموديل
    readonly_fields = [
        'invoice_no', 
        'total_before_discount', 
        'final_total', 
        'remaining_amount'
    ]

