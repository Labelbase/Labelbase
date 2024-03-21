from django import forms
from django.utils.safestring import mark_safe
from .models import Label, Labelbase


class LabelbaseForm(forms.ModelForm):
    """ """
    class Meta:
        model = Labelbase
        fields = ["name", "fingerprint", "about",  "network"]
        # We will re-introdiuce "operation_mode" in the future


class LabelForm(forms.ModelForm):
    """ """
    class Meta:
        model = Label
        fields = ["labelbase", "type", "ref", "label", "origin", "spendable"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.labelbase_id = kwargs.pop("labelbase_id")
        super(LabelForm, self).__init__(*args, **kwargs)
        user_labelbases = Labelbase.objects.filter(
            user_id=self.request.user.id, id=self.labelbase_id
        )
        self.fields["labelbase"] = forms.ModelChoiceField(
            queryset=user_labelbases,
            required=True,
            widget=forms.HiddenInput(),
        )
        if user_labelbases.count() == 1:
            self.fields["labelbase"].initial = user_labelbases[0]

        # Add the "bip329-attr" class to the labels
        for field_name in self.fields:
            self.fields[field_name].label = mark_safe(
                f'<label class="bip329-attr">{self.fields[field_name].label}</label>')
     

class ExportLabelsForm(forms.Form):
    """ """
    tx_checkbox = forms.BooleanField(required=False, initial=True, label="tx")
    addr_checkbox = forms.BooleanField(required=False, initial=True, label="addr")
    pubkey_checkbox = forms.BooleanField(required=False, initial=True, label="pubkey")
    input_checkbox = forms.BooleanField(required=False, initial=True, label="input")
    output_checkbox = forms.BooleanField(required=False, initial=True, label="output")
    xpub_checkbox = forms.BooleanField(required=False, initial=True, label="xpub")
    encrypt_checkbox = forms.BooleanField(required=False, label="encrypt")
    passphrase = forms.CharField(widget=forms.PasswordInput, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['passphrase'].disabled = True

        # Add the "bip329-attr" class to the labels of checkboxes
        for field_name in ['tx_checkbox', 'addr_checkbox', 'pubkey_checkbox',
                           'input_checkbox', 'output_checkbox', 'xpub_checkbox']:
            self.fields[field_name].label = mark_safe(
                f'<label class="bip329-attr">{self.fields[field_name].label}</label>')
