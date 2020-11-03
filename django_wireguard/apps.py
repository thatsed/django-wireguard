
from django.apps import AppConfig
from django.db import OperationalError


class SimpleVpnConfig(AppConfig):
    name = 'django_wireguard'
    verbose_name = "Django WireGuard"

    def ready(self):
        # noinspection PyUnresolvedReferences
        from django_wireguard.sync_wg import sync_wireguard_interfaces
        try:
            sync_wireguard_interfaces()
        except OperationalError:
            pass
