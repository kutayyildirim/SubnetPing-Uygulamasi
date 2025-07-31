from celery import shared_task, group
from netping.models.subnet_request import SubnetRequest
from netping.tasks.ping_ip_task import logger, ping_ip
from netping.utils.ip_helpers import get_ip_list, InvalidSubnetException


@shared_task
def start_ping_scan(subnet_request_id):
    try:
        subnet = SubnetRequest.objects.get(id=subnet_request_id)
        subnet.status = 'running'
        subnet.save()

        ip_list = get_ip_list(subnet.ip_network)

        if not ip_list:
            raise InvalidSubnetException("Boş IP listesi oluşturuldu.")

        tasks = [
            ping_ip.s(subnet.id, str(ip))
            for ip in ip_list
        ]

        job = group(tasks)
        job.apply_async()

        logger.info(f"{len(ip_list)} adet IP için ping başlatıldı.")

    except InvalidSubnetException as e:
        subnet = SubnetRequest.objects.filter(id=subnet_request_id).first()
        if subnet:
            subnet.status = 'error'
            subnet.save()
        logger.error(f"[!] Hatalı subnet: {e}")

    except SubnetRequest.DoesNotExist:
        logger.error(f"[!] SubnetRequest with id {subnet_request_id} not found.")
