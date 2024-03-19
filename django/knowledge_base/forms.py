from django import forms


class JSONUploadForm(forms.Form):
    json_file = forms.FileField(label="Knowledge Base, JSON file format") # in memory upload
