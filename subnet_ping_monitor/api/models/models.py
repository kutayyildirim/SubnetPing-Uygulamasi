from django.db import models

class SubnetRequest(models.Model):
    ip_network = models.CharField(max_length=50)
    is_ipv6 = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('running', 'Running'), ('done', 'Done'), ('error', 'Error')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_network} - {self.status}"


class PingResult(models.Model):
    subnet_request = models.ForeignKey(SubnetRequest, on_delete=models.CASCADE, related_name='ping_results')
    ip_address = models.GenericIPAddressField()
    is_alive = models.BooleanField()
    response_time_ms = models.FloatField(null=True, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} - {'Alive' if self.is_alive else 'Dead'}"
