from django.contrib import admin
from django.urls import path
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
from ..models.customers import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'assigned_rep', 'current_balance', 'is_active', 'account_actions')
    search_fields = ('name', 'phone', 'owner_name')
    list_filter = ('is_active', 'assigned_rep', 'customer_type', 'created_at')
    readonly_fields = ('current_balance', 'total_paid')

    fieldsets = (
        ("بيانات الهوية والمحل", {
            'fields': ('name', 'owner_name', 'phone', 'alt_phone', 'customer_type')
        }),
        ("الموقع الجغرافي", {
            'fields': ('address', 'latitude', 'longitude'),
            'classes': ('collapse',),
        }),
        ("السياسة المالية", {
            'fields': ('credit_limit', 'credit_days_limit'),
        }),
        ("الأرصدة الحالية", {
            'fields': ('current_balance', 'total_paid'),
        }),
        ("الإدارة والنشاط", {
            'fields': ('assigned_rep', 'is_active'),
        }),
    )

    # 1️⃣ إضافة الزرار في صفحة الجدول
    def account_actions(self, obj):
        return format_html(
            '<a class="button" href="statement/{}/" target="_blank" style="background-color: #417690; color: white; padding: 5px 10px; border-radius: 4px;">كشف الحساب 📄</a>',
            obj.pk
        )
    account_actions.short_description = "إجراءات"

    # 2️⃣ تسجيل رابط (URL) خاص بكشف الحساب داخل الأدمن
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statement/<int:customer_id>/', self.admin_site.admin_view(self.customer_statement_view)),
        ]
        return custom_urls + urls

    # 3️⃣ الدالة المعدلة بناءً على مراجعة ملفاتك (Invoice.py & payments.py)
    def customer_statement_view(self, request, customer_id):
        customer = get_object_or_404(Customer, pk=customer_id)
        
        # جلب الفواتير (استخدام related_name='invoices' والحقل 'final_total')
        invoices = customer.invoices.all().order_by('date_created')
        
        # جلب التحصيلات (استخدام related_name='payments')
        collections = customer.payments.all().order_by('collection_date')

        # دمج وترتيب الحركات
        transactions = []
        for inv in invoices:
            transactions.append({
                'date': inv.date_created,
                'desc': f"فاتورة بيع رقم {inv.invoice_no}",
                'debit': inv.final_total,  # مدين (عليه)
                'credit': 0,
            })
        
        for col in collections:
            transactions.append({
                'date': col.collection_date,
                'desc': "تحصيل نقدي",
                'debit': 0,
                'credit': col.amount,  # دائن (ليه)
            })

        # ترتيب من الأقدم للأحدث بناءً على التاريخ
        transactions.sort(key=lambda x: x['date'])

        # حساب الرصيد التراكمي
        running_balance = 0
        for tx in transactions:
            running_balance += (tx['debit'] - tx['credit'])
            tx['balance'] = running_balance

        context = {
            'customer': customer,
            'transactions': transactions,
            'final_balance': running_balance,
            'title': f"كشف حساب - {customer.name}"
        }
        return render(request, 'admin/logistics/customer_statement.html', context)

