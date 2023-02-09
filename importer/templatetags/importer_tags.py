from django import template
from importer.forms import UploadFileForm

register = template.Library()

@register.simple_tag
def bip0329labeluploadform(labelbase_id):
    form =  UploadFileForm()
    form.fields['labelbase_id'].initial = labelbase_id
    form.fields['import_type'].initial = 'BIP-0329'
    return form
