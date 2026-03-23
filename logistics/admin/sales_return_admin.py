from django.contrib import admin
from ..models.SalesReturn import SalesReturn, SalesReturnItem

class SalesReturnItemInline(admin.TabularInline):
    model = SalesReturnItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total']
    readonly_fields = ['line_total']

@admin.register(SalesReturn)
class SalesReturnAdmin(admin.ModelAdmin):
    # عرض البيانات في الجدول الرئيسي
    list_display = ['return_no', 'get_invoice_no', 'get_customer', 'total_return_amount', 'date_returned']
    search_fields = ['return_no', 'invoice__invoice_no', 'invoice__customer__name']
    list_filter = ['date_returned', 'invoice__warehouse']
    
    # حقول القراءة فقط
    readonly_fields = ['return_no', 'total_return_amount', 'date_returned']
    
    # إضافة الأصناف كـ Inline
    inlines = [SalesReturnItemInline]

    # دوال لجلب بيانات من الفاتورة المرتبطة للعرض في القائمة
    def get_invoice_no(self, obj):
        return obj.invoice.invoice_no
    get_invoice_no.short_description = 'رقم الفاتورة'

    def get_customer(self, obj):
        return obj.invoice.customer.name
    get_customer.short_description = 'العميل'

    fieldsets = (
        ('معلومات المرتجع الأساسية', {
            'fields': ('return_no', 'invoice', 'date_returned', 'reason')
        }),
        ('الأرقام المالية', {
            'fields': ('total_return_amount',)
        }),
    )

