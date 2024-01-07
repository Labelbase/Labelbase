from django import forms

IMPORTER_CHOICES = (
    ("BIP-0329", "BIP-329 .jsonl"),
    #("BIP-0329-7z-enc" , "BIP-329 (encrypted) .7z"),
    ("csv-bluewallet", "BlueWallet .csv"),
    ("csv-bitbox", "BitBox .csv"),
    ("pocket-accointing", "Pocket Accointing .csv")
)


class UploadFileForm(forms.Form):
    labelbase_id = forms.IntegerField(widget=forms.HiddenInput())
    import_type = forms.ChoiceField(
        choices=IMPORTER_CHOICES #, widget=forms.HiddenInput()
    )
    file = forms.FileField()
