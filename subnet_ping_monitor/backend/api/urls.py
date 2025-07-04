from django.urls import path
from .views import SubnetScanCreateView, SubnetPingResultListView

urlpatterns = [
    path('subnet-scan/', SubnetScanCreateView.as_view(), name='subnet-scan'),
    path('subnet-scan/<int:subnet_id>/results/', SubnetPingResultListView.as_view(), name='subnet-ping-results'),
]
