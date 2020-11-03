================
Django Wireguard
================

This is a Django app that provides management via Admin Site for WireGuard interfaces and peers.


Quick start
-----------

1. Add "django_wireguard" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django_wireguard',
    ]

2. Run ``python manage.py migrate`` to create the models.

3. Visit http://localhost:8000/admin/ to manage the VPN peers. Note: you must enable the Django Admin Site first https://docs.djangoproject.com/en/3.1/ref/contrib/admin/.


Enabling the Wagtail Integration
--------------------------------

1. Add "simple_vpn.wagtail" to your INSTALLED_APPS setting after simple_vpn::

    INSTALLED_APPS = [
        ...
        'django_wireguard'
        'django_wireguard.wagtail',
    ]

2. You can manage the VPN from the Wagtail Admin Panel Settings. ``Inspect`` a WireguardPeer object to view their configuration.


Configuration
-------------

The following settings can be provided:

* ``WIREGUARD_ENDPOINT`` the endpoint for the peer configuration. Set it to the server Public IP address or domain. Default: ``localhost``.
* ``WIREGUARD_STORE_PRIVATE_KEYS`` set this to False to disable auto generation of peer private keys. Default: ``True``.
* ``WIREGUARD_WAGTAIL_SHOW_IN_SETTINGS`` set this to False to show WireGuard models in root sidebar instead of settings panel. Default: ``True``.

Testing with Docker
-------------------

1. Make sure the WireGuard kernel modules are installed and loaded on the host machine.
2. Run `docker build -f Dockerfile.test -t django_wg_test .`
3. Run `docker run --cap-add NET_ADMIN django_wg_test`
