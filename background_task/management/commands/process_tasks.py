# -*- coding: utf-8 -*-

import random
import sys
import time
from django.core.management.base import BaseCommand
from django.utils import autoreload

from background_task.tasks import tasks, autodiscover
from background_task.utils import SignalManager
from django.db import close_old_connections
from background_task.recovery import start_recovery

import logging
logger = logging.getLogger('labelbase')


def _configure_log_std():
    class StdOutWrapper(object):
        def write(self, s):
            logger.info(s)

    class StdErrWrapper(object):
        def write(self, s):
            logger.error(s)
    sys.stdout = StdOutWrapper()
    sys.stderr = StdErrWrapper()


class Command(BaseCommand):
    help = 'Run tasks that are scheduled to run on the queue'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.sig_manager = None
        self._tasks = tasks

    def run(self, *args, **options):
        duration = options.get('duration', 0)
        sleep = options.get('sleep', 5.0)
        queue = options.get('queue', None)
        log_std = options.get('log_std', False)
        is_dev = options.get('dev', False)
        sig_manager = self.sig_manager

        if is_dev:
            # raise last Exception is exist
            autoreload.raise_last_exception()

        if log_std:
            _configure_log_std()

        autodiscover()
        start_recovery()
        start_time = time.time()
        logger.debug('BGT, startup completed')
        while (duration <= 0) or (time.time() - start_time) <= duration:
            if sig_manager.kill_now:
                # shutting down gracefully
                break

            if not self._tasks.run_next_task(queue):
                # there were no tasks in the queue, let's recover.
                close_old_connections()
                #logger.debug('waiting for tasks')
                time.sleep(sleep)
            else:
                # there were some tasks to process, let's check if there is more work to do after a little break.
                time.sleep(random.uniform(sig_manager.time_to_wait[0], sig_manager.time_to_wait[1]))

    def handle(self, *args, **options):
        is_dev = options.get('dev', False)
        self.sig_manager = SignalManager()
        if is_dev:
            reload_func = autoreload.run_with_reloader
            reload_func(self.run, *args, **options)
        else:
            self.run(*args, **options)
