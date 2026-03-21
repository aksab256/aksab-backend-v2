from django.db import models
from django.contrib.auth.models import User

class SalesRepresentative(models.Model):
    # ربط المندوب بحساب المستخدم الأساسي
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sales_rep_profile')
    
    # البيانات اللوجستية للمندوب
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    
    # كود المندوب (يُستخدم في العمليات الرسمية)
    rep_code = models.CharField(max_length=50, unique=True, editable=False)
    
    # أهداف المبيعات (Targets) مخزنة بصيغة JSON
    targets = models.JSONField(default=dict, blank=True)
    
    # تأمين عهدة الطلب (المصطلح المعتمد بدلاً من المحفظة)
    insurance_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # --- الإشعارات والربط مع Firebase ---
    # fcm_token: هو "العنوان الرقمي" لجهاز المندوب لإرسال تنبيهات العهدة والتحصيل
    fcm_token = models.TextField(null=True, blank=True)
    
    # الهيكل الإداري (المشرف المباشر)
    supervisor = models.ForeignKey(
        'SalesManager', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reps'
    )

    def save(self, *args, **kwargs):
        # توليد كود تلقائي احترافي عند أول حفظ للمندوب
        if not self.rep_code:
            # مثال: REP + آخر 4 أرقام من التليفون لسهولة التعرف
            self.rep_code = f"REP-{self.phone[-4:]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.rep_code})"

