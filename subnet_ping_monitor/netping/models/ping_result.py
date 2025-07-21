from django.db import models
from netping.models.subnet_request import SubnetRequest


class PingResult(models.Model):
    subnet_request = models.ForeignKey(SubnetRequest, on_delete=models.CASCADE, related_name='ping_results')
    ip_address = models.GenericIPAddressField()
    is_alive = models.BooleanField()
    response_time_ms = models.FloatField(null=True, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} - {'Alive' if self.is_alive else 'Dead'}"
