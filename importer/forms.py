from django import forms

class UploadFileForm(forms.Form):
    labelbase_id = forms.IntegerField()
    file = forms.FileField()
