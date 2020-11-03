from django.contrib import admin
from django.utils.safestring import mark_safe
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from django_wireguard import settings
from django_wireguard.models import WireguardPeer, WireguardInterface
from django_wireguard.forms import WireguardPeerForm


class WireguardPeerInlineAdmin(admin.TabularInline):
    model = WireguardPeer
    show_change_link = True


@modeladmin_register
class WireguardInterfaceAdmin(ModelAdmin):
    model = WireguardInterface
    menu_label = 'Wireguard Interfaces'
    menu_icon = 'lock'
    list_display = ('name', 'address', 'listen_port', 'public_key',)
    search_fields = ('name', 'address', 'listen_port')
    add_to_settings_menu = settings.WIREGUARD_WAGTAIL_SHOW_IN_SETTINGS

    inspect_view_fields = ('name', 'address')


@modeladmin_register
class WireguardPeerAdmin(ModelAdmin):
    model = WireguardPeer
    form = WireguardPeerForm
    menu_label = 'Wireguard Peers'
    menu_icon = 'lock'
    list_display = ('name', 'address', 'public_key',)
    list_filter = ()
    search_fields = ('name', 'address')
    add_to_settings_menu = settings.WIREGUARD_WAGTAIL_SHOW_IN_SETTINGS

    inspect_view_enabled = True
    inspect_template_name = 'django_wireguard/wireguardpeer_inspect.html'
    inspect_view_extra_js = ['js/qrcode.min.js', 'js/inject_qrcode.js']
    inspect_view_fields = ('name', 'address')

    def config(self, obj):
        return mark_safe(f'<pre>{obj.get_config()}</pre>')
    config.short_description = 'Config'
