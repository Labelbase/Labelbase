import logging
from background_task import background
from background_task.management.commands.remove_completed import _remove_completed_task


from labelbase.models import Label
from finances.electrum import checkup_label

logger = logging.getLogger('labelbase')


@background(schedule={'run_at': 0}, remove_existing_tasks=True)
def check_all_outputs(user_id, labelbase_id=None, loop=None):
    if labelbase_id:
        labels = Label.objects.filter(labelbase__id=labelbase_id,
                                      labelbase__user_id=user_id)
    else:
        labels = Label.objects.filter(labelbase__user_id=user_id)
    logger.debug("found {} labels".format(labels.count()))
    for label in labels:
        if label.type == "output":
            logger.debug("check_spent, label.id {}".format(label.id))
            check_spent(label.id)
    # Cleanup
    _remove_completed_task()

@background(schedule={'run_at': 0}, remove_existing_tasks=True)
def check_spent(label_id, loop=None):
    if loop:
        checkup_label(label_id, loop)
