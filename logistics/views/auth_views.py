from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from ..models import SalesRepresentative

class LoginView(APIView):
    def post(self, request):
        phone_input = request.data.get('phone')
        password_input = request.data.get('password')
        fcm_token = request.data.get('fcm_token')

        try:
            # 1. البحث في سجلات مناديب المبيعات (إدارة العهدة)
            rep = SalesRepresentative.objects.get(phone=phone_input)
            user = rep.user

            if user.check_password(password_input):
                if not user.is_active:
                    return Response({
                        "status": "error",
                        "message": "حساب المندوب معطل، يرجى مراجعة الإدارة"
                    }, status=status.HTTP_403_FORBIDDEN)

                # توليد التوكن
                token, _ = Token.objects.get_or_create(user=user)

                # تحديث توكن الإشعارات لحظياً
                if fcm_token:
                    rep.fcm_token = fcm_token
                    rep.save()

                return Response({
                    "status": "success",
                    "token": token.key,
                    "role": "sales_rep",
                    "fullname": f"{user.first_name} {user.last_name}" if user.first_name else user.username,
                    "user_id": user.id,
                    "data": {
                        "rep_code": rep.rep_code,
                        "phone": rep.phone,
                        "insurance_points": str(rep.insurance_points), # نقاط التأمين
                    }
                })
        except SalesRepresentative.DoesNotExist:
            # 2. دخول الإدارة (SuperAdmin)
            try:
                user = User.objects.get(username=phone_input)
                if user.check_password(password_input):
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({
                        "status": "success",
                        "token": token.key,
                        "role": "admin",
                        "fullname": "المدير العام للمنظومة",
                        "user_id": user.id,
                        "data": {}
                    })
            except User.DoesNotExist:
                pass

        return Response({
            "status": "error",
            "message": "بيانات الدخول غير صحيحة أو غير مسجلة بالمنظومة"
        }, status=status.HTTP_401_UNAUTHORIZED)

# --- دالة الطوارئ لإنشاء الأدمن ---
def create_admin(request):
    if not User.objects.filter(username="admin").exists():
        # الباسورد هنا هو اللي هتستخدمه للدخول أول مرة
        User.objects.create_superuser("admin", "admin@aksab.com", "aksab2026")
        return JsonResponse({"status": "admin created", "user": "admin", "pass": "aksab2026"})
    return JsonResponse({"status": "already exists"})

