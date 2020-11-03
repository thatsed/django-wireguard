from typing import Union, Optional

from django.db.models import QuerySet

from django_wireguard.models import WireguardInterface


def sync_wireguard_interfaces(queryset: Optional[Union[QuerySet, WireguardInterface]] = None):
    if queryset is None:
        queryset = WireguardInterface.objects.all()
    elif isinstance(queryset, WireguardInterface):
        queryset = [queryset]

    for interface in queryset:
        interface.wg.set_interface(private_key=interface.private_key,
                                   listen_port=interface.listen_port)

        if interface.address:
            interface.wg.set_ip_addresses(*interface.get_address_list())

        for peer in interface.peers.all():
            # update/create the wireguard peer
            interface.wg.set_peer(peer.public_key,
                                  *peer.get_interface_allowed_ips())
