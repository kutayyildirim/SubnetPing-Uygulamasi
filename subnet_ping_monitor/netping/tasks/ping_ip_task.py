from celery import shared_task
from ping3 import ping
from netping.models.ping_result import PingResult
from django.utils import timezone
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

@shared_task
def ping_ip(subnet_request_id, ip_address):
    from django.db import DatabaseError

    try:
        response_time = ping(ip_address, timeout=2)
        is_alive = response_time is not None
    except Exception:
        is_alive = False
        response_time = None

    now = timezone.now()

    try:
        PingResult.objects.create(
            subnet_request_id=subnet_request_id,
            ip_address=ip_address,
            is_alive=is_alive,
            response_time_ms=response_time * 1000 if response_time else None,
            checked_at=now
        )
        logger.info(f"[✓] Kayıt oluşturuldu: {ip_address}")
    except DatabaseError as e:
        logger.error(f"[!] PingResult insert hatası: {e}")
    except Exception as e:
        logger.error(f"[!] Diğer hata: {e}")


    cache_key = f"ping_result:{subnet_request_id}:{ip_address}"
    cache_value = {
        "ip_address": ip_address,
        "is_alive": is_alive,
        "response_time_ms": response_time * 1000 if response_time else None,
        "checked_at": now.isoformat()
    }
    cache.set(cache_key, cache_value, timeout=3600)