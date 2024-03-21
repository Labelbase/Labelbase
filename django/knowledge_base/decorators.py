from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def staff_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("You must be a staff member to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
