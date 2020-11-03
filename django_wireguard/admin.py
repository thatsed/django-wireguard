from django.contrib import admin
from django.utils.safestring import mark_safe

from django_wireguard.models import WireguardPeer, WireguardInterface
from django_wireguard.forms import WireguardPeerForm


@admin.register(WireguardInterface)
class WireguardInterfaceAdmin(admin.ModelAdmin):
    model = WireguardInterface
    list_display = ('name', 'address', 'listen_port')


@admin.register(WireguardPeer)
class WireguardPeerAdmin(admin.ModelAdmin):
    model = WireguardPeer
    form = WireguardPeerForm
    change_form_template = 'django_wireguard/wireguardpeer_change_form.html'
    list_display = ('name', 'address',)
    list_filter = ()

    def config(self, obj):
        return mark_safe(f'<pre>{obj.get_config()}</pre>')
    config.short_description = 'Config'
