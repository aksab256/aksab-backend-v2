from django.db import models
from django.contrib.auth.models import User

class SalesManager(models.Model):
    ROLE_CHOICES = [('sales_supervisor', 'مشرف'), ('sales_manager', 'مدير')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sales_manager_profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    # تعديل: السماح بترك المنطقة الجغرافية فارغة عند الإنشاء
    geographic_area = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return f"{self.get_role_display()}: {self.user.username}"
