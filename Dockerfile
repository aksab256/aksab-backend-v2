# 1. استخدام نسخة خفيفة ومستقرة من بايثون
FROM python:3.9-slim

# 2. منع بايثون من كتابة ملفات الـ pyc وتفعيل الطباعة المباشرة للـ Logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. تحديد مجلد العمل داخل الحاوية (Container)
WORKDIR /app

# 4. تثبيت مكتبات النظام الضرورية لتعريفات قاعدة البيانات والـ GCC
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. نسخ مشروعك بالكامل لداخل الحاوية
COPY . /app/

# 7. السطر السحري: 
# تنفيذ التهجير (migrate) أولاً، ثم تشغيل السيرفر (gunicorn)
# علامة && تعني: لا تشغل السيرفر إلا لو التهجير تم بنجاح
CMD python manage.py migrate && gunicorn --bind 0.0.0.0:8000 core.wsgi:application

