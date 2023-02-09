from django import template
from importer.forms import UploadFileForm

register = template.Library()

@register.simple_tag
def bip0329labeluploadform(labelbase_id):
    form =  UploadFileForm()#labelbase_id=labelbase_id)
    form.fields['labelbase_id'].initial = labelbase_id
    return form
