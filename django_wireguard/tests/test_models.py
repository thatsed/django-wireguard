import ipaddress
import warnings

from unittest import mock
from django.test import TestCase

from django_wireguard.models import WireguardInterface, WireguardPeer
from django_wireguard.wireguard import WireGuard, WireGuardException


class TestWireguardInterface(TestCase):
    interface_name = 'testInterface'

    def test_interface_creation(self):
        with self.assertRaises(WireGuardException):
            wg = WireGuard(self.interface_name)

        interface = WireguardInterface.objects.create(name=self.interface_name,
                                                      listen_port=1194,
                                                      address='10.100.20.1/24,10.100.30.1')

        try:
            wg = WireGuard(self.interface_name)
        except WireGuardException:
            self.fail("IPROUTE WireGuard Interface not created.")

        ip_addresses = wg.get_ip_addresses()
        for address in interface.get_address_list():
            ip = str(ipaddress.IPv4Interface(address))
            self.assertIn(ip, ip_addresses)
