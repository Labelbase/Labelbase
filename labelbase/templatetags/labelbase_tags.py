from django import template
from labelbase.forms import LabelbaseForm

register = template.Library()

@register.simple_tag
def labelbaseform():
    return LabelbaseForm()

@register.filter_tag
def labelbaseform(instance):
    return LabelbaseForm(instance=instance)
