from django.contrib import admin
from ..models.purchases import SupplierPayment

@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'amount', 'date', 'reference')
    list_filter = ('supplier', 'date')
    search_fields = ('supplier__name', 'reference')
    date_hierarchy = 'date'

    # اختياري: منع تعديل المبلغ بعد الحفظ لضمان دقة الحسابات
    def get_readonly_fields(self, request, obj=None):
        if obj: # لو العملية مسجلة بالفعل
            return ('supplier', 'amount', 'date')
        return ()

