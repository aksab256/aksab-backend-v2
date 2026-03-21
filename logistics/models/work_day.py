from django.db import models
from .sales_rep import SalesRepresentative

class WorkDayLog(models.Model):
    # ربط السجل بالمندوب
    rep = models.ForeignKey(
        SalesRepresentative, 
        on_delete=models.CASCADE, 
        related_name='day_logs'
    )
    
    # بيانات الوقت
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    # بيانات الموقع (بصمة جغرافية)
    start_lat = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    start_lng = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    
    end_lat = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    end_lng = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    
    # حالة اليوم (مفتوح/مغلق)
    status = models.CharField(
        max_length=20, 
        choices=[('open', 'Open'), ('closed', 'Closed')], 
        default='open'
    )

    def __str__(self):
        return f"Log {self.rep.rep_code} - {self.start_time.date()}"

