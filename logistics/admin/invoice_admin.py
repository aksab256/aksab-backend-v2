from django.contrib import admin, messages
from django.db import transaction
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
        """حفظ الأصناف والتحقق من المديونية في عملية واحدة آمنة"""
        try:
            with transaction.atomic():
                # حفظ الأصناف
                super().save_related(request, form, formsets, change)
                
                # حساب الإجماليات والتحقق من الائتمان
                instance = form.instance
                instance.update_totals()
                
        except ValidationError as e:
            # إظهار رسالة الخطأ ومنع إكمال الحفظ
            messages.error(request, str(e))
            # في حالة الخطأ، نحذف الفاتورة 'الهيكل' اللي اتكريتت عشان متبوظش الأرقام
            if not change:
                form.instance.delete()

