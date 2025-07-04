from celery import shared_task
from ping3 import ping
from .models import SubnetRequest, PingResult
from django.utils import timezone
from .utils.ip_helpers import get_ip_list, InvalidSubnetException

@shared_task
def ping_ip(subnet_request_id, ip_address):
    try:
        response_time = ping(ip_address, timeout=2)
        is_alive = response_time is not None
    except Exception:
        is_alive = False
        response_time = None

    PingResult.objects.create(
        subnet_request_id=subnet_request_id,
        ip_address=ip_address,
        is_alive=is_alive,
        response_time_ms=response_time * 1000 if response_time else None,
        checked_at=timezone.now()
    )

@shared_task
def start_ping_scan(subnet_request_id):
    try:
        subnet = SubnetRequest.objects.get(id=subnet_request_id)
        subnet.status = 'running'
        subnet.save()

        ip_list = get_ip_list(subnet.ip_network)

        for ip in ip_list:
            ping_ip.delay(subnet.id, ip)

        subnet.status = 'done'
        subnet.save()

    except InvalidSubnetException:
        subnet = SubnetRequest.objects.get(id=subnet_request_id)
        subnet.status = 'error'
        subnet.save()
    except SubnetRequest.DoesNotExist:
        pass
