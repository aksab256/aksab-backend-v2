from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # تأمين عهدة الطلب (نقاط التأمين) بدل الـ Wallet
    insurance_points = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"عهدات: {self.user.username}"

