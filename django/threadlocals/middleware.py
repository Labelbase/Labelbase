# -*- coding: utf-8 -*-
"""
threadlocals Middleware, provides a better, faster way to get at request and user.

:Authors:
   - Ben Roberts (Nutrislice, Inc.)
   - Troy Evans (Nutrislice, Inc.)
   - Herbert Poul http://sct.sphene.net
   - Bruce Kroeze

Branched from [http://code.djangoproject.com/wiki/CookBookthreadlocalsAndUser CookBookThreadLocalsAndUser]
as modified by [http://sct.sphene.net Sphene Community tools].

(see license.txt)
"""

from .threadlocals import set_thread_variable, del_thread_variables
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

class ThreadLocalMiddleware(MiddlewareMixin):
    """Middleware that puts the request object in thread local storage."""

    def process_request(self, request):
        set_thread_variable('request', request)
        # set_current_user(request.user) # not going to store user in TL's for now, since we can get it from the request if we need it, and I read somewhere that accessing reqeust.user can potentially prevent view caching from functioning correctly

    def process_response(self, request, response):
        del_thread_variables()
        return response

    def process_exception(self, request, exception):
        del_thread_variables()
