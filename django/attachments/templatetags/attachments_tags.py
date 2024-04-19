from django.template import Library
from django.urls import reverse

from ..forms import AttachmentForm
from ..models import Attachment
from ..views import add_url_for_obj

register = Library()

@register.filter(name='endswith')
def endswith(value, arg):
    """Checks if the value ends with a certain string."""
    if isinstance(value, str):
        return value.endswith(arg)
    return False

@register.inclusion_tag("attachments/add_form.html", takes_context=True)
def attachment_form(context, obj, **kwargs):
    """
    Renders a "upload attachment" form.

    The user must own ``attachments.add_attachment permission`` to add
    attachments.
    """

    return {
        "form": AttachmentForm(),
        "form_url": add_url_for_obj(obj),
        "next": context.request.path,
    }


@register.inclusion_tag("attachments/delete_link.html", takes_context=True)
def attachment_delete_link(context, attachment, **kwargs):
    if context["user"] == attachment.creator:
        return {
            "next": context.request.path,
            "delete_url": reverse(
                "attachments:delete", kwargs={"attachment_pk": attachment.pk}
            ),
        }



@register.simple_tag
def attachments_count(obj):
    """
    Counts attachments that are attached to a given object::

        {% attachments_count obj %}
    """
    attachments_count = Attachment.objects.attachments_for_object(obj).count()
    print("obj: {}, attachments_count: {}".format(obj.id, attachments_count))

    return attachments_count


@register.simple_tag
def get_attachments_for(obj, *args, **kwargs):
    """
    Resolves attachments that are attached to a given object. You can specify
    the variable name in the context the attachments are stored using the `as`
    argument.

    Syntax::

        {% get_attachments_for obj as "my_attachments" %}
    """
    return Attachment.objects.attachments_for_object(obj)
