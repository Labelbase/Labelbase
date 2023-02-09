from django import forms

IMPORTER_CHOICES = (
    ('BIP-0329', 'BIP-0329'),
    ('csv-bluewallet', 'BlueWallet .csv'),
)


class UploadFileForm(forms.Form):
    labelbase_id = forms.IntegerField(widget=forms.HiddenInput())
    import_type = forms.ChoiceField(choices=IMPORTER_CHOICES, widget=forms.HiddenInput())
    file = forms.FileField()
