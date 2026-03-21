import os
# إعدادات إضافية لحل مشكلة الـ CSRF والـ Admin
CSRF_TRUSTED_ORIGINS = ['https://aksab.pythonanywhere.com']
CORS_ALLOW_ALL_ORIGINS = True  # عشان الموبايل يعرف يكلم السيرفر بدون قيود
