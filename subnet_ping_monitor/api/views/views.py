from rest_framework import generics, status
from rest_framework.response import Response
from api.models.models import SubnetRequest, PingResult
from api.serializers.serializers import SubnetRequestSerializer, PingResultSerializer
from api.tasks import start_ping_scan
from api.utils.ip_helpers import InvalidSubnetException, get_ip_list
from rest_framework.generics import ListAPIView
from django.conf import settings
import redis
import json
from datetime import datetime


class SubnetScanCreateView(generics.CreateAPIView):
    queryset = SubnetRequest.objects.all()
    serializer_class = SubnetRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                get_ip_list(serializer.validated_data['ip_network'])
            except InvalidSubnetException as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            subnet = serializer.save()
            start_ping_scan.delay(subnet.id)

            return Response({
                'message': 'Ping taraması başlatıldı.',
                'subnet_id': subnet.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubnetPingResultListView(ListAPIView):
    serializer_class = PingResultSerializer

    def get_queryset(self):
        subnet_id = self.kwargs['subnet_id']

        r = redis.Redis(host='localhost', port=6379, db=1)

        pattern = f"ping_result:{subnet_id}:*"
        keys = r.keys(pattern)

        results = []

        for key in keys:
            value = r.get(key)
            if value:
                try:
                    data = json.loads(value)
                    results.append(PingResult(
                        subnet_request_id=subnet_id,
                        ip_address=data["ip_address"],
                        is_alive=data["is_alive"],
                        response_time_ms=data["response_time_ms"],
                        checked_at=datetime.fromisoformat(data["checked_at"])
                    ))
                except Exception:
                    continue

        if results:
            return results

        return PingResult.objects.filter(subnet_request_id=subnet_id).order_by('ip_address')
