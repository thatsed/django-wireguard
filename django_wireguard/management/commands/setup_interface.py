from ipaddress import IPv4Network

from django.core.management.base import BaseCommand
from wgnlpy import PrivateKey

from django_wireguard import settings
from django_wireguard.models import WireguardInterface


class Command(BaseCommand):
    help = 'Setup WireGuard interface'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('--port', nargs='?', type=int, default=1194)
        parser.add_argument('--private-key', nargs='?', type=str)
        parser.add_argument('--address', nargs='*', type=str)

    def handle(self, *args, **options):
        interface = WireguardInterface.objects.filter(name=options['name'])

        address = ','.join(options['address'] or []) or None

        if interface.exists():
            if options['private_key']:
                interface.update(port=options['port'],
                                 private_key=options['private_key'],
                                 address=address)
            else:
                interface.update(port=options['port'],
                                 address=address)
        else:
            interface = WireguardInterface.objects.create(name=options['name'],
                                                          private_key=options['private_key'],
                                                          address=address)

        self.stderr.write(self.style.SUCCESS(f"Interface setup completed: {interface.name}.\n"))
