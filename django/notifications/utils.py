from django.contrib.auth.models import User
from messages_extends.models import Message
from messages_extends import constants
"""
DEBUG = 10
INFO = 20
SUCCESS = 25
WARNING = 30
ERROR = 40

DEBUG_PERSISTENT = 11
INFO_PERSISTENT = 21
SUCCESS_PERSISTENT = 26
WARNING_PERSISTENT = 31
ERROR_PERSISTENT = 41

DEBUG_STICKY = 12
INFO_STICKY = 22
SUCCESS_STICKY = 27
WARNING_STICKY = 32
ERROR_STICKY = 42

"""
def notify_user(username, message, level=constants.SUCCESS_PERSISTENT):
    u = User.objects.get(username=username)
    m = Message(user=u, message=message, level=level)
    m.save()

def notify_success_persistent(username, message):
    notify_user(username, message, level=constants.SUCCESS_PERSISTENT)

def notify_warning_persistent(username, message):
    notify_user(username, message, level=constants.WARNING_PERSISTENT)

def notify_error_persistent(username, message):
    notify_user(username, message, level=constants.ERROR_PERSISTENT)

def notify_error(username, message):
    notify_user(username, message, level=constants.ERROR)
