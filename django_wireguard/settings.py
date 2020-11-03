from django.conf import settings

WIREGUARD_ENDPOINT = getattr(settings, 'WIREGUARD_ENDPOINT', 'localhost')
WIREGUARD_STORE_PRIVATE_KEYS = getattr(settings, 'WIREGUARD_STORE_PRIVATE_KEYS', True)
