from django.contrib import admin, messages
from ..models.Invoice import Invoice
from ..models.InvoiceItem import InvoiceItem
from django.core.exceptions import ValidationError

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    fields = ['product', 'unit_price', 'quantity', 'discount_per_unit', 'line_total']
    readonly_fields = ['line_total']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_no', 'customer', 'salesman', 'final_total', 'payment_method', 'date_created']
    readonly_fields = ['invoice_no', 'total_before_discount', 'final_total', 'remaining_amount']
    inlines = [InvoiceItemInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        instance = form.instance
        
        # تشغيل المحرك الرئيسي للحسابات والمديونية
        instance.update_totals()
        
        # التحقق من حدود الائتمان بعد ما عرفنا المبالغ الحقيقية
        try:
            instance.full_clean()
        except ValidationError as e:
            messages.error(request, str(e))
            # ملحوظة: الفاتورة اتسيفت بس العميل هيطلع له تحذير، 
            # لو عايز تمسحها برمجياً لو فشلت ممكن تضيف instance.delete()

