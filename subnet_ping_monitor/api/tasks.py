from celery import shared_task
from ping3 import ping
from api.models.models import SubnetRequest, PingResult
from django.utils import timezone
from api.utils.ip_helpers import get_ip_list, InvalidSubnetException
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

@shared_task
def ping_ip(subnet_request_id, ip_address):
    try:
        response_time = ping(ip_address, timeout=2)
        is_alive = response_time is not None
    except Exception:
        is_alive = False
        response_time = None

    now = timezone.now()

    PingResult.objects.create(
        subnet_request_id=subnet_request_id,
        ip_address=ip_address,
        is_alive=is_alive,
        response_time_ms=response_time * 1000 if response_time else None,
        checked_at=now
    )

    cache_key = f"ping_result:{subnet_request_id}:{ip_address}"
    cache_value = {
        "ip_address": ip_address,
        "is_alive": is_alive,
        "response_time_ms": response_time * 1000 if response_time else None,
        "checked_at": now.isoformat()
    }
    cache.set(cache_key, cache_value, timeout=3600)


@shared_task
def start_ping_scan(subnet_request_id):
    try:
        subnet = SubnetRequest.objects.get(id=subnet_request_id)
        subnet.status = 'running'
        subnet.save()

        ip_list = get_ip_list(subnet.ip_network)

        if not ip_list:
            raise InvalidSubnetException("Boş IP listesi oluşturuldu.")

        for ip in ip_list:
            logger.info(f"Pinging: {ip}")
            ping_ip.delay(subnet.id, str(ip))

        subnet.status = 'done'
        subnet.save()

    except InvalidSubnetException as e:
        subnet = SubnetRequest.objects.filter(id=subnet_request_id).first()
        if subnet:
            subnet.status = 'error'
            subnet.save()
    except SubnetRequest.DoesNotExist:
        logger.error(f"SubnetRequest with id {subnet_request_id} does not exist.")
