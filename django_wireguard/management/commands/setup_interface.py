from django.core.management.base import BaseCommand

from django_wireguard.models import WireguardInterface


class Command(BaseCommand):
    help = 'Setup WireGuard interface'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('--listen-port', nargs='?', type=int, default=1194)
        parser.add_argument('--private-key', nargs='?', type=str)
        parser.add_argument('--address', nargs='*', type=str)

    def handle(self, *args, **options):
        interface = WireguardInterface.objects.filter(name=options['name'])

        address = ','.join(options['address'] or [])

        if interface.exists():
            if options['private_key']:
                interface.update(listen_port=options['listen_port'],
                                 private_key=options['private_key'],
                                 address=address)
            else:
                interface.update(listen_port=options['listen_port'],
                                 address=address)
            self.stderr.write(self.style.SUCCESS(f"Interface updated: {interface.first().name}.\n"))
        else:
            interface = WireguardInterface.objects.create(name=options['name'],
                                                          listen_port=options['listen_port'],
                                                          private_key=options['private_key'],
                                                          address=address)

            self.stderr.write(self.style.SUCCESS(f"Interface created: {interface.name}.\n"))
