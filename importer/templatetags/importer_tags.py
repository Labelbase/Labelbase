from django import template
from importer.forms import UploadFileForm

register = template.Library()

@register.simple_tag
def labeluploadform():
    return UploadFileForm()
