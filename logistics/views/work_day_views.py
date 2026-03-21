from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from ..models import SalesRepresentative, WorkDayLog

class WorkDayAPIView(APIView):
    def post(self, request):
        rep_code = request.data.get('rep_code')
        action = request.data.get('action') # 'start' or 'end'
        lat = request.data.get('lat')
        lng = request.data.get('lng')

        try:
            rep = SalesRepresentative.objects.get(rep_code=rep_code)
            
            if action == 'start':
                # التأكد إنه مفيش يوم مفتوح بالفعل
                active_log = WorkDayLog.objects.filter(rep=rep, status='open').first()
                if active_log:
                    return Response({"message": "يوجد وردية مفتوحة بالفعل"}, status=400)
                
                WorkDayLog.objects.create(
                    rep=rep,
                    start_lat=lat,
                    start_lng=lng,
                    status='open'
                )
                return Response({"status": "success", "message": "تم بدء الوردية"})

            elif action == 'end':
                active_log = WorkDayLog.objects.filter(rep=rep, status='open').first()
                if not active_log:
                    return Response({"message": "لا يوجد وردية مفتوحة لإنهائها"}, status=400)
                
                active_log.end_time = timezone.now()
                active_log.end_lat = lat
                active_log.end_lng = lng
                active_log.status = 'closed'
                active_log.save()
                return Response({"status": "success", "message": "تم إنهاء الوردية"})

        except SalesRepresentative.DoesNotExist:
            return Response({"message": "المندوب غير مسجل"}, status=404)
        
        return Response({"message": "إجراء غير صالح"}, status=400)

