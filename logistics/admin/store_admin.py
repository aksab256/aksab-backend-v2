from django.contrib import admin
from ..models.store import Store # تأكد من اسم الموديل والمسار

class StoreAdmin(admin.ModelAdmin):
    list_display = ('supermarket_name', 'store_type', 'is_active')
    search_fields = ('supermarket_name',)
