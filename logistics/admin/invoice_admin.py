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
    list_display = ['invoice_no', 'customer', 'final_total', 'payment_method', 'date_created', 'print_invoice']
    list_filter = ['warehouse', 'payment_method', 'date_created', 'salesman']
    
    # تأكد إن الحقول المحسوبة للقراءة فقط عشان متبوظش الحسبة اليدوية
    readonly_fields = ['invoice_no', 'date_created', 'total_before_discount', 'final_total', 'remaining_amount']
    
    fieldsets = (
        ('بيانات الفاتورة الأساسية', {
            'fields': (('invoice_no', 'date_created'), ('customer', 'warehouse'), ('salesman', 'collector'))
        }),
        ('الحسابات المالية', {
            'fields': (
                ('total_before_discount', 'discount_amount'),
                ('final_total', 'payment_method'),
                ('paid_amount', 'remaining_amount')
            )
        }),
    )

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
        context = {
            'invoice': invoice,
            'items': items,
            'title': f"فاتورة رقم {invoice.invoice_no}",
        }
        return render(request, 'admin/logistics/invoice_print.html', context)

    # ⚠️ التعديل هنا: حذفنا التكرار اللي كان بيسبب خصم مرتين
    def save_related(self, request, form, formsets, change):
        try:
            with transaction.atomic():
                super().save_related(request, form, formsets, change)
                # مفيش داعي ننادي update_totals هنا لأن InvoiceItem.save بيقوم بالواجب
        except Exception as e:
            messages.error(request, f"⚠️ خطأ: {str(e)}")

