import ipaddress

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django_wireguard.wireguard import PrivateKey, PublicKey


def validate_private_ipv4(value):
    try:
        ip_address = ipaddress.IPv4Address(value)
        if not ip_address.is_private or ip_address.is_unspecified:
            raise ValueError
    except (ValueError, ipaddress.AddressValueError):
        raise ValidationError(
            _('%(value)s is not a valid private IP Address.'),
            params={'value': value},
        )


def validate_allowed_ips(value):
    for ip in value.split(','):
        try:
            ip_address = ipaddress.IPv4Interface(ip)
            if not ip_address.is_private or ip_address.is_unspecified:
                raise ValueError
        except (ValueError, ipaddress.AddressValueError):
            raise ValidationError(
                _('%(value)s is not a valid private IP Address.'),
                params={'value': value},
            )


def validate_wireguard_private_key(value):
    try:
        PrivateKey(value)
    except ValueError:
        raise ValidationError(
            _('The value specified is not a valid WireGuard Private Key.'),
        )


def validate_wireguard_public_key(value):
    try:
        PublicKey(value)
    except ValueError:
        raise ValidationError(
            _('The value specified is not a valid WireGuard Public Key.'),
        )
