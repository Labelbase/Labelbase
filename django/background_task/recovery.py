import logging 
from datetime import timedelta


logger = logging.getLogger("labelbase")


def reset_task(task, delay_runtime=0):
    task.attempts = 0
    task.failed_at = None
    task.locked_at = None
    task.last_error = ""
    task.locked_by = None
    task.run_at += timedelta(seconds=delay_runtime)
    task.save()


def start_recovery():
    from background_task.models import Task
    locked_tasks = Task.objects.filter(locked_by__isnull=False)
    for task in locked_tasks:
        if not task.locked_by_pid_running():
            reset_task(task)
            logger.debug(f"Reset Task with id={task.id} {task.task_name} – done")

    if Task.objects.filter(locked_by__isnull=False):
        logger.debug("Startup of BGT completed (non-empty).")
    else:
        logger.debug("Startup of BGT completed (empty).")

    logger.info("Startup of BGT completed")
