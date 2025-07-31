from django.urls import path
from .views.subnet_scan_create_view import SubnetScanCreateView
from .views.subnet_ping_result_list_view import SubnetPingResultListView

#celery -A pingmonitor worker -l info --pool=solo, python manage.py runserver
#import redis
#r = redis.Redis(host='localhost', port=6379, db=0)
# r.flushdb()
urlpatterns = [
    path('subnet-scan/', SubnetScanCreateView.as_view(), name='subnet-scan'),
    path('subnet-scan/<int:subnet_id>/results/', SubnetPingResultListView.as_view(), name='subnet-ping-results'),
]
