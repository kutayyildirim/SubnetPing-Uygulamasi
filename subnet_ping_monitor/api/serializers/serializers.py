from rest_framework import serializers
from api.models.models import SubnetRequest, PingResult

class SubnetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubnetRequest
        fields = ['id', 'ip_network', 'is_ipv6', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

class PingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PingResult
        fields = ['ip_address', 'is_alive', 'response_time_ms', 'checked_at']