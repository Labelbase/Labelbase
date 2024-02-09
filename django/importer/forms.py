from django import forms
from .models import IMPORTER_CHOICES


class UploadFileForm(forms.Form):
    labelbase_id = forms.IntegerField(widget=forms.HiddenInput())
    import_type = forms.ChoiceField(
        choices=IMPORTER_CHOICES
    )
    file = forms.FileField()
