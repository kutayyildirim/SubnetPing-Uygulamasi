from celery import shared_task
from netping.models.ping_result import PingResult
from django.utils import timezone
from django.core.cache import cache
from django.db import DatabaseError
import subprocess
import platform
import logging

logger = logging.getLogger(__name__)


def ping_ip_address(ip, timeout=2):

    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'

    ping_args = ['ping']


    if ':' in ip:
        ping_args.append('-6')

    ping_args += [param, '1', timeout_param, str(timeout), ip]

    try:
        result = subprocess.run(
            ping_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        success = result.returncode == 0
        ms = extract_time_ms(result.stdout)
        return success, ms
    except Exception as e:
        logger.error(f"[!] Ping subprocess hatası: {e}")
        return False, None


def extract_time_ms(output):

    try:
        for line in output.splitlines():
            if "time=" in line:
                time_part = line.split("time=")[-1].split(" ")[0]
                return float(time_part)
    except Exception:
        pass
    return None


@shared_task
def ping_ip(subnet_request_id, ip_address):
    try:
        is_alive, response_time = ping_ip_address(ip_address, timeout=2)
    except Exception as e:
        logger.error(f"[!] Ping sırasında hata: {e}")
        is_alive = False
        response_time = None

    now = timezone.now()

    try:
        PingResult.objects.create(
            subnet_request_id=subnet_request_id,
            ip_address=ip_address,
            is_alive=is_alive,
            response_time_ms=response_time,
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
        "response_time_ms": response_time,
        "checked_at": now.isoformat()
    }
    cache.set(cache_key, cache_value, timeout=3600)
