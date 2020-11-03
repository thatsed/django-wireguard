from django.core.management.base import BaseCommand, CommandError
from wgnlpy import PrivateKey, PublicKey

from django_wireguard import settings
from django_wireguard.models import WireguardPeer, WireguardInterface


class Command(BaseCommand):
    help = 'Create a WireGuard Peer'

    def add_arguments(self, parser):
        parser.add_argument('interface', type=str, help="interface's name")
        parser.add_argument('name', type=str, help="peer's name")
        parser.add_argument('-f', '--forward-traffic', action='store_true', help="forward traffic through VPN")
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--private-key', nargs='?', type=str, help="specify the private key for the peer.")
        group.add_argument('--public-key', nargs='?', type=str, help="specify the public key for the peer.")

    def handle(self, *args, **options):
        name = options['name']
        try:
            interface = WireguardInterface.objects.get(name=options['interface'])
        except WireguardInterface.DoesNotExist:
            raise CommandError("Requested interface does not exist.")

        if options['private_key'] is None and options['public_key'] is None:
            private_key = PrivateKey.generate()
            public_key = private_key.public_key()
        elif options['public_key'] is None:
            try:
                private_key = PrivateKey(options['private_key'])
            except ValueError:
                raise CommandError("Invalid Private Key.")
            public_key = private_key.public_key()
        else:
            try:
                public_key = PublicKey(options['public_key'])
            except ValueError:
                raise CommandError("Invalid Public Key.")
            private_key = None

        if WireguardPeer.objects.filter(public_key=public_key).exists():
            raise CommandError("A peer with the same key already exists.")

        peer = WireguardPeer(name=name,
                             interface=interface,
                             private_key=private_key,
                             public_key=public_key,
                             forward_traffic=options['forward_traffic'])

        if not settings.WIREGUARD_STORE_PRIVATE_KEYS and private_key is not None:
            self.stderr.write(self.style.NOTICE("Removing Private Key references before adding peer."))
            peer.private_key = None

        # save peer before configuration to get it an IP address
        peer.save()

        # if peer didn't save private key and it's available, temporarily add it to generate conf with it
        if peer.private_key is None and private_key is not None:
            peer.private_key = private_key

        self.stderr.write(self.style.SUCCESS("\nPeer configuration:"
                                             "\n-------------------\n"))
        self.stdout.write(peer.get_config())
        self.stderr.write('\n\n')

        self.stderr.write(self.style.SUCCESS(f"Peer added successfully: {name}.\n"))
