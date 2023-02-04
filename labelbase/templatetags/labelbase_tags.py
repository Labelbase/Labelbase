from django import template
from labelbase.forms import LabelbaseForm

register = template.Library()


def labelbaseform():
    return LabelbaseForm()

register.tag('labelbaseform', labelbaseform)
