from django.urls import path
from .views.views import SubnetScanCreateView, SubnetPingResultListView
#celery -A pingmonitor worker -l info --pool=solo, python manage.py runserver
#import redis
#r = redis.Redis(host='localhost', port=6379, db=0)
# r.flushdb()
urlpatterns = [
    path('subnet-scan/', SubnetScanCreateView.as_view(), name='subnet-scan'),
    path('subnet-scan/<int:subnet_id>/results/', SubnetPingResultListView.as_view(), name='subnet-ping-results'),
]
