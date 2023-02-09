from django import forms

IMPORT_CHOICES = (
    ('BIP-0329', 'BIP-0329'),
    ('csv-bluewallet', 'BlueWallet .csv'),
)


class UploadFileForm(forms.Form):
    labelbase_id = forms.IntegerField()
    import_type = forms.ChoiceField(choices = IMPORT_CHOICES)
    file = forms.FileField()
