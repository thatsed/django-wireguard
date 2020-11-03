
from django.apps import AppConfig
from django.db import OperationalError


class DjangoWireguardConfig(AppConfig):
    name = 'django_wireguard'
    verbose_name = "Django WireGuard"

    def ready(self):
        # noinspection PyUnresolvedReferences
        from django_wireguard.sync_wg import sync_wireguard_interfaces
        try:
            sync_wireguard_interfaces()
        except OperationalError:
            pass


class DjangoWireguardWagtailConfig(AppConfig):
    name = 'django_wireguard.wagtail'
    label = 'django_wireguard_wagtail'
    verbose_name = "Django WireGuard Wagtail Integration"
