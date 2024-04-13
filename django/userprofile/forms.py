from django import forms
from .models import Profile


class ProfileAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar_url']
        labels = {
            'avatar_url': 'Paste the URL of your avatar image (JPEG, PNG, or GIF)',
        }


class MempoolForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['mempool_endpoint']
        labels = {
            'mempool_endpoint': 'Mempool Endpoint',
        }


class ElectrumServerInfoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['electrum_hostname', 'electrum_ports',
                    'electrum_hostname_test', 'electrum_ports_test']
        labels = {
            'electrum_hostname': 'Electrum Hostname (Mainnet)',
            'electrum_ports': 'Electrum Protocol + Port (Mainnet)',
            'electrum_hostname_test': 'Electrum Hostname (Testnet)',
            'electrum_ports_test': 'Electrum Protocol + Port (Testnet)',
        }




class ProfileCurrencyForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['my_currency']


#
