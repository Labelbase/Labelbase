import random
import sys
import time
from django.core.management.base import BaseCommand
from django.utils import autoreload
import asyncio
import threading

from background_task.tasks import tasks, autodiscover
from background_task.utils import SignalManager
from django.db import close_old_connections
from background_task.recovery import start_recovery

import logging
logger = logging.getLogger('labelbase')


class Command(BaseCommand):
    help = 'Run tasks that are scheduled to run on the queue'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.sig_manager = None
        self._tasks = tasks

    def create_event_loop(self):
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def close_event_loop(self):
        if self.loop:
            self.loop.close()

    def run(self, *args, **options):
        duration = options.get('duration', 0)
        sig_manager = self.sig_manager
        autodiscover()
        start_recovery()
        self.create_event_loop()
        start_time = time.time()
        logger.debug('BGT, startup completed')
        try:
            while (duration <= 0) or (time.time() - start_time) <= duration:
                if sig_manager.kill_now:
                    # shutting down gracefully
                    break
                assert self.loop
                if not self._tasks.run_next_task(queue=None, loop=self.loop):
                    # there were no tasks in the queue, let's recover.
                    close_old_connections()
                    time.sleep(5) # Wait a few second before checking again.
                else:
                    # there were some tasks to process, let's check if there is more work to do after a little break.
                    sleep_duration = random.uniform(sig_manager.time_to_wait[0],
                                                    sig_manager.time_to_wait[1])
                    time.sleep(sleep_duration)
        finally:
            self.close_event_loop()

    def handle(self, *args, **options):
        self.sig_manager = SignalManager()
        self.run(*args, **options)
