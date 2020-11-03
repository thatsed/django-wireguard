from django.core.management.base import BaseCommand

from django_wireguard.models import WireguardPeer


class Command(BaseCommand):
    help = 'Create a WireGuard Peer'

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument('pubkeys', type=str, nargs='+', help="peer's public key")
        group.add_argument('--all', action='store_true', help="delete all peers")

    def handle(self, *args, **options):
        public_keys = options['pubkeys']
        delete_all = options['all']

        if delete_all:
            peers = WireguardPeer.objects.all()
        else:
            peers = WireguardPeer.objects.filter(public_key__in=public_keys)

        if not peers.exists():
            self.stderr.write(self.style.NOTICE("No peer deleted."))
            return

        peer_names = '\n'.join(peer.name for peer in peers)
        peers.delete()
        self.stderr.write(self.style.SUCCESS(f"Deleted peers:\n"
                                             f"--------------\n"
                                             f"{peer_names}\n"))
