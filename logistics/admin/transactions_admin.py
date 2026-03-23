from django.contrib import admin
from ..models.payments import Collection

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    # تحسين العرض ليشمل بيانات أكثر تفصيلاً
    list_display = ['collection_date', 'customer', 'get_amount_display', 'collector', 'invoice_link']
    list_filter = ['collection_date', 'collector', 'invoice__warehouse'] # فلتر بالمخزن مهم للمراجعة
    search_fields = ['customer__name', 'invoice__invoice_no', 'collector__username']
    
    # تحسين تجربة البحث
    autocomplete_fields = ['customer', 'invoice']
    
    # جعل التاريخ للقراءة فقط لو العملية قديمة لضمان عدم التلاعب
    readonly_fields = ['collection_date']

    def get_amount_display(self, obj):
        return f"{obj.amount} ج.م"
    get_amount_display.short_description = 'المبلغ المحصل'

    def invoice_link(self, obj):
        if obj.invoice:
            return f"فاتورة: {obj.invoice.invoice_no}"
        return "تحصيل دفعة حساب"
    invoice_link.short_description = 'المرجع'

    def save_model(self, request, obj, form, change):
        """تلقائية تسجيل المحصل"""
        if not obj.pk and not obj.collector:
            obj.collector = request.user
        
        # هنا نقطة مهمة: التأكد أن العميل هو صاحب الفاتورة فعلياً
        if obj.invoice and obj.customer != obj.invoice.customer:
            from django.core.exceptions import ValidationError
            raise ValidationError("⚠️ خطأ: العميل المختار ليس هو صاحب الفاتورة المحددة!")
            
        super().save_model(request, obj, form, change)

