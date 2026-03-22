from django.contrib import admin
from ..models.Invoice import Invoice
from ..models.InvoiceItem import InvoiceItem

# ده عشان يخليك تضيف وتشوف الأصناف جوه صفحة الفاتورة نفسها (Inline)
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0 # مبيضيفش سطور فاضية زيادة
    readonly_fields = ['line_total'] # عشان تتحسب أوتوماتيك ومحدش يعدلها يدوي

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_no', 'customer', 'salesman', 'final_total', 'payment_method', 'date_created']
    list_filter = ['payment_method', 'date_created', 'salesman']
    search_fields = ['invoice_no', 'customer__name', 'salesman__username']
    inlines = [InvoiceItemInline] # ربط الأصناف بالفاتورة
    readonly_fields = ['remaining_amount', 'date_created'] # حقول للقراءة فقط

    # تقسيم الحقول في صفحة الإضافة بشكل منظم
    fieldsets = (
        ('بيانات الأساسية', {
            'fields': ('invoice_no', 'customer', 'salesman', 'collector')
        }),
        ('الموقع الجغرافي', {
            'fields': ('lat', 'lng'),
            'classes': ('collapse',) # بتبقى مخفية وممكن تفتحها
        }),
        ('الحسابات المالية', {
            'fields': ('total_before_discount', 'discount_amount', 'tax_amount', 'final_total', 'payment_method', 'paid_amount', 'remaining_amount')
        }),
        ('إضافات', {
            'fields': ('notes', 'is_synced_to_platform')
        }),
    )

