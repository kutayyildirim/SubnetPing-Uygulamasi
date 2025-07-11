from rest_framework import serializers
from netping.models.ping_result import PingResult


class PingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PingResult
        fields = ['ip_address', 'is_alive', 'response_time_ms', 'checked_at']
