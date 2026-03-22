from django.contrib import admin
from ..models.payments import Collection  # ✅ غيرنا دي من transactions لـ payments

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['collection_date', 'customer', 'amount', 'collector', 'invoice']
    list_filter = ['collection_date', 'collector']
    search_fields = ['customer__name', 'invoice__invoice_no']
    autocomplete_fields = ['customer', 'invoice']

    def save_model(self, request, obj, form, change):
        if not obj.pk: 
            obj.collector = request.user 
        super().save_model(request, obj, form, change)

