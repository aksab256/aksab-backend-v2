from django.contrib import admin
from django.utils.html import format_html
from ..models.expenses import ExpenseCategory, Expense

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    # أضفنا حقل الـ image_tag هنا
    list_display = ('category', 'amount', 'date', 'user', 'receipt_preview')
    list_filter = ('category', 'date')
    readonly_fields = ('user', 'date', 'receipt_preview')

    def receipt_preview(self, obj):
        if obj.receipt_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 5px;" />', obj.receipt_image.url)
        return "لا يوجد صورة"
    receipt_preview.short_description = "معاينة الإيصال"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

