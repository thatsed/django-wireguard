import base64
import ipaddress
from enum import Enum
from typing import Optional, List, Union

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from pyroute2 import WireGuard as PyRouteWireGuard, IPRoute


class PublicKey:
    """
    X25519 PrivateKey Object.
    Returns both private and public keys base64encoded.
    If a base64encoded `private_key` is not given, a new one will be generated.
    """
    __slots__ = ('__public_key',)

    def __init__(self, public_key: Union[str, X25519PublicKey]):
        if isinstance(public_key, X25519PublicKey):
            self.__public_key = public_key
        elif isinstance(public_key, str):
            self.__public_key = X25519PublicKey.from_public_bytes(base64.b64decode(public_key))
        else:
            raise TypeError("public_key must be a string or X25519PublicKey object")

    def __str__(self):
        value = base64.b64encode(
            self.__public_key.public_bytes(serialization.Encoding.Raw,
                                           serialization.PublicFormat.Raw))
        if isinstance(value, bytes):
            value = value.decode('ascii')
        return value


class PrivateKey:
    """
    X25519 PrivateKey Object.
    Returns both private and public keys base64encoded.
    """
    __slots__ = ('__private_key',)

    def __init__(self, private_key: Union[str, X25519PrivateKey]):
        if isinstance(private_key, X25519PrivateKey):
            self.__private_key = private_key
        elif isinstance(private_key, str):
            self.__private_key = X25519PrivateKey.from_private_bytes(base64.b64decode(private_key))
        else:
            raise TypeError("private_key must be a string or X25519PrivateKey object")

    @classmethod
    def generate(cls):
        return cls(X25519PrivateKey.generate())

    def __str__(self):
        value = base64.b64encode(
            self.__private_key.private_bytes(serialization.Encoding.Raw,
                                             serialization.PrivateFormat.Raw,
                                             serialization.NoEncryption()))
        if isinstance(value, bytes):
            value = value.decode('ascii')
        return value

    def public_key(self) -> PublicKey:
        return PublicKey(self.__private_key.public_key())


class WireGuardException(Exception):
    pass


class WireGuard:
    __slots__ = ('__ifname', '__ifindex')
    __wg = None
    __ipr = None

    class ErrorCode(Enum):
        NO_SUCH_DEVICE = 19

    def __init__(self, interface_name):
        self.__connect_backend()
        self.__ifname = interface_name
        interface = self.__get_interface_index(interface_name)
        if not interface:
            raise WireGuardException("Interface does not exist.")
        self.__ifindex = interface

    @classmethod
    def __connect_backend(cls):
        if cls.__wg is None:
            cls.__wg = PyRouteWireGuard()
        if cls.__ipr is None:
            cls.__ipr = IPRoute()

    @classmethod
    def create_interface(cls, interface_name: str) -> 'WireGuard':
        cls.__connect_backend()
        cls.__ipr.link('add', ifname=interface_name, kind='wireguard')
        return cls(interface_name)

    @classmethod
    def get_or_create_interface(cls, interface_name: str) -> 'WireGuard':
        cls.__connect_backend()
        interface = cls.__get_interface_index(interface_name)
        if not interface:
            return cls.create_interface(interface_name)
        return cls(interface_name)

    @classmethod
    def __get_interface_index(cls, interface_name: str) -> Optional[int]:
        cls.__connect_backend()
        interface: list = cls.__ipr.link_lookup(ifname=interface_name)
        if not interface:
            return None
        return interface[0]

    @property
    def interface_name(self):
        return self.__ifname

    def get_ip_addresses(self) -> List[str]:
        interface_data = self.__ipr.get_addr(label=self.interface_name)
        return list(map(
            lambda i: dict(i['attrs'])['IFA_ADDRESS'] + '/' + str(i['prefixlen']),
            interface_data
        ))

    def set_ip_addresses(self, *ip_addresses):
        old_ip_addresses = self.get_ip_addresses()
        new_ip_addresses = []
        for address in ip_addresses:
            try:
                address = ipaddress.IPv4Interface(address)
            except Exception as e:
                raise ValueError(e)

            new_ip_addresses.append(str(address))

        for address in old_ip_addresses:
            ip, mask = address.split('/')
            if address not in new_ip_addresses:
                self.__ipr.addr('del', self.__ifindex,
                                address=ip, mask=int(mask))

        for address in new_ip_addresses:
            ip, mask = address.split('/')
            if address not in old_ip_addresses:
                self.__ipr.addr('add', self.__ifindex,
                                address=ip, mask=int(mask))

    def set_interface(self, **kwargs):
        self.__wg.set(self.__ifname, **kwargs)

    def set_peer(self, public_key, *allowed_ips, **kwargs):
        self.set_interface(peer={
            'public_key': str(public_key),
            'allowed_ips': [str(ipaddress.IPv4Interface(ip)) for ip in allowed_ips],
            **kwargs
        })

    def set_peers(self, *peers):
        for peer in peers:
            self.set_interface(peer=peer)

    def remove_peers(self, *public_keys):
        for pubkey in public_keys:
            peer = {'public_key': str(pubkey), 'remove': True}
            self.set_interface(peer=peer)
