from django import forms
from .models import Profile

class ProfileAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar_url']
        labels = {
            'avatar_url': 'Paste the URL of your avatar image (JPEG, PNG, or GIF)',
        }

class ElectrumServerInfoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['electrum_hostname', 'electrum_ports']
        labels = {
            'electrum_hostname': 'Electrum Hostname',
            'electrum_ports': 'Electrum Protocol + Port',
        }



class ProfileCurrencyForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['my_currency']



#
