import ipaddress
from typing import List

from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from django_wireguard import settings
from django_wireguard.utils import clean_comma_separated_list
from django_wireguard.validators import validate_private_ipv4, validate_wireguard_private_key, \
    validate_wireguard_public_key, validate_allowed_ips

from django_wireguard.wireguard import WireGuard, PrivateKey


__all__ = ('WireguardInterface', 'WireguardPeer')


class WireguardInterface(models.Model):
    name = models.CharField(max_length=100,
                            validators=[RegexValidator(r'^[A-z0-9]+$',
                                                       _("Interface Name must be a string of alphanumeric chars."))],
                            unique=True,
                            verbose_name=_("Interface Name"))
    listen_port = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(65535)],
                                              verbose_name=_("Listen Port"))
    address = models.TextField(blank=True,
                               validators=[validate_allowed_ips],
                               verbose_name=_("Interface addresses."))
    private_key = models.CharField(max_length=64,
                                   blank=True,
                                   validators=[validate_wireguard_private_key],
                                   verbose_name=_("Private Key (leave empty to auto generate)"))

    class Meta:
        verbose_name = _("WireGuard Interface")
        verbose_name_plural = _("WireGuard Interfaces")

    @property
    def public_key(self) -> str:
        return str(PrivateKey(self.private_key).public_key())

    @property
    def wg(self):
        return WireGuard.get_or_create_interface(self.name)

    def __repr__(self):
        return f"{self._meta.verbose_name} {self.name}"

    def __str__(self):
        return f"{self.name} - {self.address}"

    def get_address_list(self):
        return clean_comma_separated_list(self.address)

    def get_endpoint(self):
        return f"{settings.WIREGUARD_ENDPOINT}:{self.listen_port}"


class WireguardPeer(models.Model):
    interface = models.ForeignKey(WireguardInterface,
                                  on_delete=models.CASCADE,
                                  related_name='peers',
                                  verbose_name=_("Interface"))

    name = models.CharField(max_length=100,
                            blank=False)
    private_key = models.CharField(max_length=64,
                                   null=True,
                                   blank=True,
                                   validators=[validate_wireguard_private_key],
                                   verbose_name=_("Peer's Private Key"))
    public_key = models.CharField(max_length=64,
                                  unique=True,
                                  blank=True,
                                  validators=[validate_wireguard_public_key],
                                  verbose_name=_("Peer's Public Key"))
    dns = models.TextField(blank=True, verbose_name=_("DNS"),
                           validators=[validate_allowed_ips],
                           help_text=_("Comma separated list."))
    # Peer's IP inside the VPN network
    address = models.CharField(validators=[validate_private_ipv4],
                               max_length=20,
                               blank=True,
                               verbose_name=_("Address"))
    interface_allowed_ips = models.TextField(validators=[validate_allowed_ips],
                                             blank=True,
                                             verbose_name=_("Interface Allowed IPs"),
                                             help_text=_("One per line"))
    allowed_ips = models.TextField(validators=[validate_allowed_ips],
                                   blank=True,
                                   verbose_name=_("Allowed IPs"),
                                   help_text=_("Comma separated list."))
    interface_persistent_keepalive = models.PositiveIntegerField(blank=True,
                                                                 default=0,
                                                                 verbose_name=_("Interface Persistent Keepalive"))
    persistent_keepalive = models.PositiveIntegerField(blank=True,
                                                       default=0,
                                                       verbose_name=_("Persistent Keepalive"))

    class Meta:
        verbose_name = _("WireGuard Peer")
        verbose_name_plural = _("WireGuard Peers")
        unique_together = ('interface', 'name')

    def __repr__(self):
        return f"{self._meta.verbose_name} {self.name} - interface {self.interface}"

    def __str__(self):
        return f"{self.name}@{self.interface.name} - {self.address}"

    def get_dns_list(self) -> List[str]:
        return clean_comma_separated_list(self.dns)

    def get_allowed_ips(self) -> List[str]:
        return clean_comma_separated_list(self.allowed_ips)

    def get_interface_allowed_ips(self) -> List[str]:
        values = clean_comma_separated_list(self.interface_allowed_ips)
        if self.address:
            values.append(self.address)
        return values

    def get_config(self) -> str:
        """
        Generate WireGuard configuration for peer as string.

        If ``WIREGUARD_STORE_PRIVATE_KEYS`` is False, the string
        ``<INSERT-PRIVATE-KEY-FOR:{public_key}>`` will be placed as PrivateKey.

        :return: Peer configuration as string.
        """
        private_key = self.private_key or _('<INSERT-PRIVATE-KEY-FOR:%(pubkey)s>') % {'pubkey': self.public_key}

        config = f"[Interface]\n" \
                 f"Address={self.address}/32\n" \
                 f"PrivateKey={private_key}\n"

        if self.dns:
            config += f"DNS={self.dns}\n"

        config += f"[Peer]\n" \
                  f"Endpoint={self.interface.get_endpoint()}\n" \
                  f"PublicKey={self.interface.public_key}\n" \
                  f"AllowedIPs={self.allowed_ips}"

        return config


@receiver(pre_save, sender=WireguardInterface)
def sync_wireguard_interface(sender, **kwargs):
    interface = kwargs['instance']
    if not interface.private_key:
        interface.private_key = str(PrivateKey.generate())

    interface.wg.set_interface(private_key=interface.private_key,
                               listen_port=interface.listen_port)

    interface.wg.set_ip_addresses(*interface.get_address_list())


@receiver(pre_save, sender=WireguardPeer)
def sync_wireguard_peer(sender, **kwargs):
    peer: WireguardPeer = kwargs['instance']
    interface = peer.interface

    if not peer.address:
        for address in interface.wg.get_ip_addresses():
            address = ipaddress.IPv4Interface(address)
            interface_address = str(address.ip)
            subnet = address.network

            # fetch other peers for checks
            peers = WireguardPeer.objects.all().only('address')

            # auto assign IP address
            peer_addresses = [peer.address for peer in peers]
            peer_addresses.append(interface_address)
            if not peer.address:
                for host in subnet.hosts():
                    if str(host) not in peer_addresses:
                        peer.address = str(host)
                        break
                else:
                    continue
            break
        else:
            raise RuntimeWarning("WireGuard interface's subnets have no available IP left")

    if not peer.private_key and not peer.public_key:
        if settings.WIREGUARD_STORE_PRIVATE_KEYS:
            peer.private_key = str(PrivateKey.generate())
        else:
            # this shouldn't happen with standard form, but manual creation could lead here
            raise RuntimeError("WIREGUARD_STORE_PRIVATE_KEYS is False, yet no key has been passed.")

    # generate and store public key if the private key is provided
    if peer.private_key:
        peer.public_key = str(PrivateKey(peer.private_key).public_key())

    # update/create the wireguard peer
    interface.wg.set_peer(peer.public_key,
                          *peer.get_interface_allowed_ips())


@receiver(pre_delete, sender=WireguardPeer)
def delete_peer(sender, **kwargs):
    peer: WireguardPeer = kwargs['instance']
    peer.interface.wg.remove_peers(peer.public_key)
