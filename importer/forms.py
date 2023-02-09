from django import forms

IMPORT_CHOICES = (
    ('BIP-0329', 'BIP-0329'),
    ('csv-bluewallet', 'BlueWallet .csv'),
)


class UploadFileForm(forms.Form):
    labelbase_id = forms.IntegerField()
    import_type = forms.ChoiceField(choices = IMPORT_CHOICES, widget = forms.HiddenInput())
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.fields['labelbase_id'].initial = kwargs.pop('labelbase_id')
