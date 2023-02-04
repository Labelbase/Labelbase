from django import template
from labelbase.forms import LabelbaseForm

register = template.Library()

@register.simple_tag
def labelbaseform():
    return LabelbaseForm()

@register.simple_tag
def labelbaseform(instance):
    return LabelbaseForm(instance=instance)
