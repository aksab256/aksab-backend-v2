from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
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
    list_display = ['invoice_no', 'customer', 'final_total', 'payment_method', 'date_created', 'print_invoice']
    list_filter = ['warehouse', 'payment_method', 'date_created', 'salesman']
    readonly_fields = ['invoice_no', 'date_created', 'total_before_discount', 'final_total', 'remaining_amount']
    
    inlines = [InvoiceItemInline]

    def print_invoice(self, obj):
        return format_html(
            '<a class="button" href="print/{}/" target="_blank" style="background-color: #27ae60; color: white;">طباعة 🖨️</a>',
            obj.pk
        )
    print_invoice.short_description = "الطباعة"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('print/<uuid:invoice_id>/', self.admin_site.admin_view(self.invoice_print_view)),
        ]
        return custom_urls + urls

    def invoice_print_view(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        items = invoice.items.all()
        context = {'invoice': invoice, 'items': items, 'title': f"فاتورة رقم {invoice.invoice_no}"}
        return render(request, 'admin/logistics/invoice_print.html', context)

    # ⛔ لا تضع هنا دالة save_related أبداً لمنع التكرار

