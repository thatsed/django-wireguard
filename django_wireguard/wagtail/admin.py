from django.contrib import admin
from django.utils.safestring import mark_safe
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from django_wireguard.models import WireguardPeer
from django_wireguard.forms import WireguardPeerForm


@modeladmin_register
class WireguardPeerAdmin(ModelAdmin):
    model = WireguardPeer
    form = WireguardPeerForm
    menu_label = 'VPN'
    menu_icon = 'locked'
    list_display = ('name', 'address')
    list_filter = ()
    search_fields = ('name', 'private_vpn_ip')

    inspect_view_enabled = True
    inspect_template_name = 'django_wireguard/wireguardpeer_inspect.html'
    inspect_view_extra_js = ['js/qrcode.min.js', 'js/inject_qrcode.js']
    inspect_view_fields = ('name', 'address')

    def config(self, obj):
        return mark_safe(f'<pre>{obj.get_config()}</pre>')
    config.short_description = 'Config'
