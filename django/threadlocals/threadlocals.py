# -*- coding: utf-8 -*-
"""
__init__ module for the threadlocals package

Derived from django-threaded-multihost (see license.txt)
"""
__docformat__ = "restructuredtext"

import logging

log = logging.getLogger('threadlocals.middleware')

from threading import local

_threadlocals = local()
_threadvariables = set()


def set_thread_variable(key, val):
    _threadvariables.add(key)
    setattr(_threadlocals, key, val)


def get_thread_variable(key, default=None):
    return getattr(_threadlocals, key, default)


def del_thread_variable(key):
    if hasattr(_threadlocals, key):
        delattr(_threadlocals, key)


def del_thread_variables():
    for key in _threadvariables:
        del_thread_variable(key)


def get_current_request():
    return get_thread_variable('request', None)


def get_current_session():
    req = get_current_request()
    if req is None:
        return None
    return req.session


def get_current_user():
    user = get_thread_variable('user', None)
    if user is None:
        req = get_current_request()
        if req == None or not hasattr(req, 'user'):
            return None
        user = req.user
    return user


def set_current_user(user):
    set_thread_variable('user', user)


def set_request_variable(key, val, use_threadlocal_if_no_request=True):
    request = get_current_request()
    if not request:
        if not use_threadlocal_if_no_request:
            raise RuntimeError(
                "Unable to set request variable. No request available in threadlocals. Is ThreadLocalMiddleware installed?")
        set_thread_variable(key, val)
    else:
        try:
            var_store = getattr(request, '_variables')
        except AttributeError:
            setattr(request, '_variables', {})
            var_store = getattr(request, '_variables')
        var_store[key] = val


def get_request_variable(key, default=None, use_threadlocal_if_no_request=True):
    request = get_current_request()
    if not request:
        if not use_threadlocal_if_no_request:
            raise RuntimeError(
                "Unable to get request variable. No threadlocal request available. Is ThreadLocalMiddleware installed?")
        else:
            return get_thread_variable(key, default)
    return request._variables.get(key, default) if hasattr(request, '_variables') else default

