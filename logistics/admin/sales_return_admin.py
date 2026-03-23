from django.contrib import admin
from ..models.SalesReturn import SalesReturn, SalesReturnItem

class SalesReturnItemInline(admin.TabularInline):
    model = SalesReturnItem
    extra = 1
    # 🆕 التحديث: إضافة selected_unit وتفعيل autocomplete
    fields = ['product', 'selected_unit', 'quantity', 'unit_price', 'line_total']
    readonly_fields = ['line_total']
    autocomplete_fields = ['product']

@admin.register(SalesReturn)
class SalesReturnAdmin(admin.ModelAdmin):
    # عرض البيانات في الجدول الرئيسي
    list_display = ['return_no', 'get_invoice_no', 'get_customer', 'total_return_amount', 'date_returned']
    search_fields = ['return_no', 'invoice__invoice_no', 'invoice__customer__name']
    list_filter = ['date_returned', 'invoice__warehouse']
    
    # حقول القراءة فقط
    readonly_fields = ['return_no', 'total_return_amount', 'date_returned']
    
    inlines = [SalesReturnItemInline]

    fieldsets = (
        ('معلومات المرتجع الأساسية', {
            'fields': (('return_no', 'date_returned'), ('invoice', 'reason'))
        }),
        ('الأرقام المالية للمرتجع', {
            'fields': ('total_return_amount',)
        }),
    )

    # دوال العرض الذكية
    def get_invoice_no(self, obj):
        return obj.invoice.invoice_no
    get_invoice_no.short_description = 'رقم الفاتورة'

    def get_customer(self, obj):
        return obj.invoice.customer.name
    get_customer.short_description = 'العميل'

    # 🆕 حقن سكريبت الباركود لسهولة المرتجعات
    class Media:
        js = (
            'https://unpkg.com/html5-qrcode/html5-qrcode.min.js',
            'js/admin_barcode_scanner.js',
        )


