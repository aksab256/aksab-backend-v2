from django.apps import AppConfig

class LogisticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logistics'

    def ready(self):
        # السطر ده هو "المفتاح" اللي بيشغل الـ Signals
        import logistics.signals 

