from celery import shared_task
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
