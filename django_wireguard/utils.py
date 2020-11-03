from typing import List


def purge_private_keys() -> int:
    """Purge all Private Key from database.

    :return: Removed keys count.
    """
    from django_wireguard.models import WireguardPeer

    peers = WireguardPeer.objects.filter(private_key__isnull=False)
    if peers.exists():
        peers.update(private_key=None)

    return peers.count()


def clean_comma_separated_list(value: str) -> List[str]:
    values = (value
              .replace(' ', '')
              .replace('\n\r', '')
              .replace('\n', '')
              .split(','))

    if '' in values:
        values.remove('')

    return values
