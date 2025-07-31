from ipaddress import ip_network, IPv4Network, IPv6Network

class InvalidSubnetException(Exception):
    pass


def get_ip_list(subnet_str: str):

    try:
        net = ip_network(subnet_str, strict=False)
    except ValueError:
        raise InvalidSubnetException("Geçersiz IP/Subnet formatı.")

    if isinstance(net, IPv4Network):
        if net.prefixlen < 24:
            raise InvalidSubnetException("IPv4 için en büyük izin verilen subnet mask değeri /24'tür.")
    elif isinstance(net, IPv6Network):
        if net.prefixlen < 96:
            raise InvalidSubnetException("IPv6 için en büyük izin verilen subnet mask değeri /96'dır.")
    else:
        raise InvalidSubnetException("Sadece IPv4 ve IPv6 adresleri desteklenmektedir.")

    return [str(ip) for ip in net.hosts()]
