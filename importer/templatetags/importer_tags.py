from django import template
from importer.forms import UploadFileForm

register = template.Library()

@register.simple_tag
def bip0329labeluploadform(labelbase_id):
    return UploadFileForm(labelbase_id=labelbase_id, format="bip0329")
