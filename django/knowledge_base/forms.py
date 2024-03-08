from django import forms


class JSONUploadForm(forms.Form):
    json_file = forms.FileField() # in memory upload
