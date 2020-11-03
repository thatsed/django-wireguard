from django import forms
from django.utils.translation import ugettext_lazy as _

from django_wireguard import settings
from django_wireguard.models import WireguardPeer


class WireguardPeerForm(forms.ModelForm):
    class Meta:
        model = WireguardPeer
        help_texts = {}
        if settings.WIREGUARD_STORE_PRIVATE_KEYS:
            fields = '__all__'
            help_texts.update({
              'private_key': _("Leave blank to generate one automatically. "
                               "You may specify only the Public Key for good security, but you'll have to generate "
                               "your own Private Key to place inside the configuration."),
              'public_key': _("Leave empty if Private Key is used instead (or left empty too for auto generation).")
            })
        else:
            exclude = ('private_key',)
            help_texts.update({
              'public_key': _("Generate a Private Key first, then place here the associated Public Key. "
                              "To learn more, follow the official WireGuard guide: "
                              "https://www.wireguard.com/quickstart/#key-generation")
            })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['public_key'].required = not settings.WIREGUARD_STORE_PRIVATE_KEYS

    def clean(self):
        cleaned_data = super().clean()
        private_key = cleaned_data.get('private_key')
        public_key = cleaned_data.get('public_key')
        if private_key and public_key:
            self.add_error('public_key', _("Public Key is not required when Private Key is specified."))
        
        if not settings.WIREGUARD_STORE_PRIVATE_KEYS and not public_key:
            self.add_error('public_key', _("Enable WIREGUARD_STORE_PRIVATE_KEYS for "
                                           "automatic key handling, but keep in mind that doing so impacts security "
                                           "considerably."))
