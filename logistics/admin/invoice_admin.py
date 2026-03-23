from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
from django.db import transaction
from ..models.Invoice import Invoice
from ..models.InvoiceItem import InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['product', 'selected_unit', 'unit_price', 'quantity', 'discount_per_unit', 'line_total']
    readonly_fields = ['line_total']
    autocomplete_fields = ['product']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    search_fields = ['invoice_no', 'customer__name']
    # أضفنا print_invoice للقائمة
    list_display = ['invoice_no', 'customer', 'final_total', 'payment_method', 'date_created', 'print_invoice']
    list_filter = ['warehouse', 'payment_method', 'date_created', 'salesman']
    readonly_fields = ['invoice_no', 'date_created', 'total_before_discount', 'final_total', 'remaining_amount']
    
    inlines = [InvoiceItemInline]

    # 1️⃣ زرار الطباعة في الجدول
    def print_invoice(self, obj):
        return format_html(
            '<a class="button" href="print/{}/" target="_blank" style="background-color: #27ae60; color: white;">طباعة 🖨️</a>',
            obj.pk
        )
    print_invoice.short_description = "الطباعة"

    # 2️⃣ تسجيل رابط الطباعة
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('print/<uuid:invoice_id>/', self.admin_site.admin_view(self.invoice_print_view)),
        ]
        return custom_urls + urls

    # 3️⃣ منطق تجميع بيانات الفاتورة وأصنافها
    def invoice_print_view(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        # جلب الأصناف المرتبطة بالفاتورة
        items = invoice.items.all() 
        
        context = {
            'invoice': invoice,
            'items': items,
            'title': f"فاتورة رقم {invoice.invoice_no}",
        }
        return render(request, 'admin/logistics/invoice_print.html', context)

    def save_related(self, request, form, formsets, change):
        try:
            with transaction.atomic():
                super().save_related(request, form, formsets, change)
                instance = form.instance
                instance.update_totals()
        except Exception as e:
            messages.error(request, f"⚠️ خطأ في الحفظ: {str(e)}")
            if not change and instance.pk:
                instance.delete()

