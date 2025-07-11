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