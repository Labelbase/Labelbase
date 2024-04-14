from django import template
from background_task.models import Task

register = template.Library()

@register.simple_tag
def is_label_id_in_queue(label_id):
    return Task.objects.filter(task_name="finances.tasks.check_spent",
                                    task_params__contains=label_id).exists()
