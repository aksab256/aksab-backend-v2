from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from ..models.sales_rep import SalesRepresentative

# لو في Inline خليه يعرض الـ user بس لحد ما نتأكد من الحقول التانية
class SalesRepresentativeInline(admin.StackedInline):
    model = SalesRepresentative
    can_delete = False
    fields = ('user',) # شيلنا warehouse و target_amount مؤقتاً

# تعديل كلاس الـ Admin الأساسي للمناديب
@admin.register(SalesRepresentative)
class SalesRepresentativeAdmin(admin.ModelAdmin):
    # هنعرض الـ user بس عشان نتخطى خطأ الـ E108
    list_display = ('user',) 

