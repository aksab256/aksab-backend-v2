from django.contrib import admin
from ..models.payments import Collection  # ✅ الاستدعاء من ملف payments

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['collection_date', 'customer', 'amount', 'collector', 'invoice']
    list_filter = ['collection_date', 'collector']
    search_fields = ['customer__name', 'invoice__invoice_no']
    autocomplete_fields = ['customer', 'invoice']

    def save_model(self, request, obj, form, change):
        """
        تعديل ذكي: 
        1. لو المستخدم اختار محصل بإيده -> بنحفظ اللي اختاره.
        2. لو ساب الخانة فاضية وهو بيكريت العملية -> بنسجل المستخدم الحالي كمحصل.
        """
        if not obj.pk and not obj.collector:
            obj.collector = request.user
            
        super().save_model(request, obj, form, change)

