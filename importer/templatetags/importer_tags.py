from django import template
from importer.forms import UploadFileForm

register = template.Library()

@register.simple_tag
def bip0329labeluploadform(labelbase_id):
    return UploadFileForm()
