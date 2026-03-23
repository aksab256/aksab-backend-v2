from django.contrib import admin
from ..models.purchases import SupplierPayment

@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'amount', 'date', 'reference')
    list_filter = ('supplier', 'date')
    search_fields = ('supplier__name', 'reference')
    date_hierarchy = 'date'

    # منع تعديل البيانات المالية بعد الحفظ لضمان سلامة الحسابات
    def get_readonly_fields(self, request, obj=None):
        if obj: # في حالة التعديل (السجل موجود مسبقاً)
            return ('supplier', 'amount', 'date')
        return ()

