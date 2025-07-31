import json
from datetime import datetime
import redis
from rest_framework.generics import ListAPIView
from netping.models.ping_result import PingResult
from netping.serializers.ping_result_serializer import PingResultSerializer


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
