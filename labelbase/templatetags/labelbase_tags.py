from django import template
from labelbase.forms import LabelbaseForm

register = template.Library()


def labelbaseform(instance=None):
    return LabelbaseForm(instance=instance)

register.filter('labelbaseform', labelbaseform)
