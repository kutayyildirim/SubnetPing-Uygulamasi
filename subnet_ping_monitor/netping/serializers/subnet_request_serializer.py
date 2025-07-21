from rest_framework import serializers
from netping.models.subnet_request import SubnetRequest


class SubnetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubnetRequest
        fields = ['id', 'ip_network', 'is_ipv6', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']